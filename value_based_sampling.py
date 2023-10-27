import numpy as np
import vtk
from mpi4py import MPI
from vtk.util.numpy_support import vtk_to_numpy

# Input values
p = 0.001
bin_num = 16


comm = MPI.COMM_WORLD

rank = comm.Get_rank()
size = comm.Get_size()


# Performs simple random sampling
def simple_rs (np_arr, prob):
    return np.where( np.random.rand( *tuple(np_arr.shape) ) < prob, np_arr, np.nan )

# Counts the number of values lying between min_arr[i], max_arr[i]
# for all 'i' in data, and returns a numpy array.
def freq_count(data, min_arr, max_arr):
    bin_counts = list(range(bin_num))
    for i in range(bin_num):
        bin_counts[i] = np.sum( np.logical_and( min_arr[i] <= data , data <= max_arr[i] ) )
    return bin_counts

# Gives the importance function based on histogram and sampling rate
def get_imp_fn(global_bin_counts, bin_num, data_length, prob):
    imp_fn = list(range(bin_num))

    sorted_idx = np.argsort(global_bin_counts)
    sample_count = int(data_length * prob)
    min_bin_samples = sample_count / bin_num

    # if rank == 0:
    #     print(sample_count, min_bin_samples)

    cur_bin_num = bin_num
    
    j = 0
    while j < bin_num:
        bin_count = global_bin_counts[sorted_idx[j]]
        # if rank == 0:
        #     print(f"bin_count: {bin_count}, min_bin_samples: {min_bin_samples}")
        #     print(f"data_length: {data_length}, cur_bin_count: {cur_bin_num}")

        if bin_count < min_bin_samples:
            imp_fn[sorted_idx[j]] = bin_count
            data_length -= bin_count
            cur_bin_num -= 1
            min_bin_samples = data_length / cur_bin_num
            j += 1
        else:
            for k in range(j, bin_num):
                # if rank == 0:
                #     print(f"on_index: {sorted_idx[k]}, min_bin_samples: {min_bin_samples}")
                imp_fn[sorted_idx[k]] = min_bin_samples
            break
    
    for j in range(bin_num):
        imp_fn[j] /= global_bin_counts[j]
    
    return imp_fn

def value_bs(data, min_arr, max_arr, imp_fn):
    rand_data = np.random.rand( *tuple(data.shape) )
    for i in range(len(imp_fn)):
        indices = np.where( np.logical_and(min_arr[i] <= data, data <= max_arr[i]) )
        data[indices] = np.where( rand_data[indices] < imp_fn[i], data[indices], np.nan )

data = None
dims = None
data_dtype = None
final_data = None

# Currently the entire data is being read on
# one machine and sent to all other machines.
# Could we parallely read from all machines
# and just gather the result in one machine?
if rank == 0:
    # Reading the data in node with rank 0
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName("Isabel_Pressure_Large.vti")
    reader.Update()
    imageData = reader.GetOutput()

    data = vtk_to_numpy(imageData.GetPointData().GetScalars())
    dims = imageData.GetDimensions()
    data = data.reshape(dims[2], dims[1], dims[0])
    data = data.transpose(2, 1, 0)
    data = np.copy(data, order='C')

    dims = tuple(data.shape)
    print("Dims of data:", dims)
    data_dtype = data.dtype

    # Numpy array to receive the final processed data at rank 0
    final_data = np.empty(dims, order='C', dtype=data_dtype)

# Broadcasting dimensions to calculate length of receiving buffer
dims = comm.bcast(dims, root=0)
data_dtype = comm.bcast(data_dtype, root=0)
length = dims[0] * dims[1] * dims[2]

counts = []

quo = int(length / size)
rem = length % size
for i in range(size):
    counts.append(quo)
    if rem > i:
        counts[-1] = counts[-1] + 1

# Scattering the data
recvbuf = np.empty(counts[rank], order='C', dtype=data_dtype)
comm.Scatterv(data, recvbuf, root=0)

# Calculating ranges of bins
max_val = np.max(recvbuf)
min_val = np.min(recvbuf)

max_val = comm.reduce(max_val, op=MPI.MAX, root=0)
min_val = comm.reduce(min_val, op=MPI.MIN, root=0)

min_arr = list(range(0, bin_num))
max_arr = list(range(0, bin_num))

if rank == 0:
    jump = (max_val - min_val) / bin_num
    min_arr[0] = min_val
    max_arr[0] = min_val + jump

    for i in range(1, bin_num):
        min_arr[i] = min_arr[i-1] + jump
        max_arr[i] = max_arr[i-1] + jump

max_arr = comm.bcast(max_arr, root=0)
min_arr = comm.bcast(min_arr, root=0)

# Getting the frequency distribution
bin_counts = freq_count(recvbuf, min_arr, max_arr)

# Reducing the frequency distribution to get the global distribution
global_bin_counts = np.copy(bin_counts, order='C')
bin_counts = np.array(bin_counts, order='C')

comm.Allreduce(bin_counts, global_bin_counts, op=MPI.SUM)

# Calculating the sampling probabilities at all nodes
imp_fn = get_imp_fn(global_bin_counts, bin_num, length, p)

if rank == 0:
    print(imp_fn)
    print(flush=True)

# Value based random sampling
value_bs(recvbuf, min_arr, max_arr, imp_fn)

# # Simple random sampling
# sendbuf = simple_rs(recvbuf, p)

# Gathering the data
comm.Gatherv(recvbuf, final_data, root=0)

if rank == 0:
    print("Gathered everything")

    # Checking if the samples points and locations are same as in original array
    test_arr = np.invert( np.isnan(final_data) )
    sampled_num = np.sum( test_arr )
    
    print(f"{sampled_num} sampled out of {length} data points. Sampling rate: {sampled_num/length}")

    out_arr = final_data[ test_arr.nonzero() ] - data[ test_arr.nonzero() ]
    print("0 value of next 2 outputs indicates that sampled values are equal to original values:", np.min(out_arr), np.max(out_arr))

MPI.Finalize()
