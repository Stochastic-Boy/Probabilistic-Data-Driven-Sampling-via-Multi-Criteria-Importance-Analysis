from vtk import vtkPoints, vtkCellArray, vtkFloatArray, vtkPolyData, vtkXMLDataSetWriter, vtkXMLImageDataReader
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np

# Read 3D volume data from a vtk image file
def read_vtk_image(file_name):
    # Reading the data in node with rank 0
    reader = vtkXMLImageDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    imageData = reader.GetOutput()

    # Converting data to numpy array retaining the dimensions
    data = vtk_to_numpy(imageData.GetPointData().GetScalars())
    dims = imageData.GetDimensions()
    spacing = imageData.GetSpacing()
    data = data.reshape(dims[2], dims[1], dims[0])
    data = data.transpose(2, 1, 0)
    return data, dims, spacing

# 'coords': n x 3 numpy ndarry with coordinates
# 'vals': n x 1 numpy ndarray with values
# 'out_file_name': Name of vtp file generated
# Saves the given data in vtp format
def save_to_vtp(coords, vals, out_file_name):
    print(f"Writing to {out_file_name}")

    # Create the points array
    points = vtkPoints()
    pids = [points.InsertNextPoint(x) for x in coords]

    # Create the cell array
    vertices = vtkCellArray()
    [vertices.InsertNextCell(1, [x]) for x in pids]

    # Create the array of float scalars
    point_data = vtkFloatArray()
    point_data.SetNumberOfComponents(1)
    point_data.SetName("Values")
    [point_data.InsertNextTuple((x,)) for x in vals]

    # Create the polydata file
    poly_data = vtkPolyData()
    poly_data.SetPoints(points)
    poly_data.SetVerts(vertices)
    poly_data.GetPointData().AddArray(point_data)
    poly_data.GetPointData().SetActiveScalars(point_data.GetName())

    # Writing to file
    writer = vtkXMLDataSetWriter()
    writer.SetFileName(out_file_name)
    writer.SetInputData(poly_data)
    writer.Write()

    print(f"Written to {out_file_name}.")

# Takes a 3D numpy array and returns values and corresponding coordinates
def get_coords_and_vals(data, spacing, data_dtype='float32'):
    coords = np.empty((data.size, 3), order='C', dtype='float32')
    vals = np.empty((data.size,), order='C', dtype=data_dtype)

    idx = 0
    it = np.nditer(data, flags=['multi_index'])
    for x in it:
        if not np.isnan(x):
            coords[idx, :] =  np.array(it.multi_index)
            vals[idx] = x
            idx = idx + 1
    coords = coords[:idx, :]
    vals = vals[:idx]

    spacing = np.array(spacing, dtype='float32').reshape(1, 3)
    coords = coords * spacing
    return coords, vals

# Counts the number of values lying between min_arr[i], max_arr[i]
# for all 'i' in data, and returns a numpy array.
def freq_count(data, min_arr, max_arr):
    assert len(min_arr) == len(max_arr)

    bin_num = len(max_arr)
    bin_counts = list(range(bin_num))
    for i in range(bin_num):
        bin_counts[i] = np.sum( np.logical_and( min_arr[i] <= data , data <= max_arr[i] ) )
    return bin_counts

# Gives the value based importance function based on histogram and sampling rate
def get_val_imp_fn(global_bin_counts, bin_num, data_length, prob):
    imp_fn = list(range(bin_num))

    sorted_idx = np.argsort(global_bin_counts)
    sample_count = int(data_length * prob)
    min_bin_samples = sample_count / bin_num

    
    # print(sample_count, min_bin_samples)

    cur_bin_num = bin_num
    
    j = 0
    while j < bin_num:
        bin_count = global_bin_counts[sorted_idx[j]]
        
        # print(f"bin_count: {bin_count}, min_bin_samples: {min_bin_samples}")
        # print(f"data_length: {data_length}, cur_bin_count: {cur_bin_num}")

        if bin_count < min_bin_samples:
            imp_fn[sorted_idx[j]] = bin_count
            sample_count -= bin_count
            cur_bin_num -= 1
            min_bin_samples = sample_count / cur_bin_num
            j += 1
        else:
            for k in range(j, bin_num):
                
                # print(f"on_index: {sorted_idx[k]}, min_bin_samples: {min_bin_samples}")
                imp_fn[sorted_idx[k]] = min_bin_samples
            break
    
    for j in range(bin_num):
        imp_fn[j] /= global_bin_counts[j]
    
    # print(flush=True)
    
    return imp_fn

# Gives the importance function based on histogram and sampling rate
def get_grad_imp_fn(global_bin_counts, bin_num, data_length, prob):
    imp_fn = list(np.zeros(bin_num))

    sample_count = int(data_length * prob)
    j = bin_num - 1
    while j >= 0 and sample_count > 0:
        bin_count = global_bin_counts[j]
        imp_fn[j] = min(bin_count, sample_count)
        sample_count = sample_count - bin_count
        j = j-1

    for j in range(bin_num):
        imp_fn[j] /= global_bin_counts[j]
    
    return imp_fn

# Performs simple random sampling
def simple_rs (np_arr, prob):
    return np.where( np.random.rand( *tuple(np_arr.shape) ) < prob, np_arr, np.nan )

def value_bs(data, min_arr, max_arr, imp_fn):
    bin_freq = np.empty(len(imp_fn))
    samp_freq = np.empty(len(imp_fn))
    rand_data = np.random.rand( *tuple(data.shape) )
    for i in range(len(imp_fn)):
        indices = np.where( np.logical_and(min_arr[i] <= data, data <= max_arr[i]) )
        bin_freq[i] = indices[0].size # Number of elements in the bin
        data[indices] = np.where( rand_data[indices] < imp_fn[i], data[indices], np.nan )
        samp_freq[i] = np.sum( np.invert( np.isnan(data[indices]) ) ) # Number of elements sampled from each bin
    return bin_freq, samp_freq

def grad_bs(data, grads, min_arr, max_arr, imp_fn):
    bin_freq = np.empty(len(imp_fn))
    samp_freq = np.empty(len(imp_fn))
    rand_data = np.random.rand( *tuple(data.shape) )
    for i in range(len(imp_fn)):
        indices = np.where( np.logical_and(min_arr[i] <= grads, grads <= max_arr[i]) )
        bin_freq[i] = indices[0].size # Number of elements in the bin
        data[indices] = np.where( rand_data[indices] < imp_fn[i], data[indices], np.nan )
        samp_freq[i] = np.sum( np.invert( np.isnan(data[indices]) ) ) # Number of elements sampled from each bin
    return bin_freq, samp_freq
