import numpy as np
import vtk
from mpi4py import MPI
from vtk.util.numpy_support import vtk_to_numpy

# Input values
p = 0.05

comm = MPI.COMM_WORLD

rank = comm.Get_rank()
size = comm.Get_size()


def simple_rs (np_arr, prob):
    return np.where( np.random.rand( *tuple(np_arr.shape) ) < prob, np_arr, np.nan )


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

# Simple random sampling
sendbuf = simple_rs(recvbuf, p)

# Gathering the data
comm.Gatherv(sendbuf, final_data, root=0)

if rank == 0:
    print("Gathered everything")

    # Checking if the samples points and locations are same as in original array
    test_arr = np.invert( np.isnan(final_data) ).nonzero()
    out_arr = final_data[ test_arr ] - data[ test_arr ]
    print(np.min(out_arr), np.max(out_arr))

MPI.Finalize()
