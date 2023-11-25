import numpy as np
from mpi4py import MPI
from optparse import OptionParser

from utils import *

comm = MPI.COMM_WORLD

rank = comm.Get_rank()
size = comm.Get_size()

def main(in_file_name, p, out_file_name, verbose, track_time):
    data = None
    dims = None
    spacing = None
    data_dtype = None
    final_data = None

    split_sizes = None
    split_sizes_input = None
    disp_input = None
    split_sizes_output = None
    disp_output = None

    start_time = None
    reading_time = None
    scatter_time = None
    comp_time = None
    gather_time = None
    saving_time = None
    total_time = None

    # Currently the entire data is being read on
    # one machine and sent to all other machines.
    # Could we parallely read from all machines
    # and just gather the result in one machine?
    if rank == 0:
        print(f"Running on {size} processes")
        print(flush=True)

        if (track_time == True) and (rank == 0):
            start_time = MPI.Wtime()

        print("Reading VTK image...", flush=True)
        data, dims, spacing = read_vtk_image(in_file_name)
        data = data.astype('float64', order='C')
        print("Completed reading")
        print(flush=True)

        # Storing information about the data
        dims = tuple(data.shape)
        data_dtype = data.dtype
        print("Dimensions of data:", dims)
        print("Dtype of data:", data_dtype)
        print(flush=True)

        if (track_time == True) and (rank == 0):
            reading_time = MPI.Wtime()

        # Numpy array to receive the final processed data at rank 0
        final_data = np.empty(dims, order='C', dtype='float64')

        # Creating the data split_sizes
        split = np.array_split( np.arange(0, dims[0]), size, axis=0)
        split_sizes = []
        for i in range(0, len(split)):
            split_sizes = np.append(split_sizes, len(split[i]))
        
        # split sizes and displacements
        split_sizes_input = split_sizes * dims[1] * dims[2]
        disp_input = np.insert(np.cumsum(split_sizes_input),0,0)[0:-1]

        split_sizes_output = split_sizes * dims[1] * dims[2]
        disp_output = np.insert(np.cumsum(split_sizes_input),0,0)[0:-1]

    # Broadcasting dimensions to calculate length of receiving buffer
    # Broadcasting metadata, split sizes and displacements
    dims = comm.bcast(dims, root=0)
    spacing = comm.bcast(spacing, root=0)
    data_dtype = comm.bcast(data_dtype, root=0)
    split_sizes = comm.bcast(split_sizes, root=0)
    split_sizes_input = comm.bcast(split_sizes_input, root=0)
    disp_input = comm.bcast(disp_input, root=0)

    length = dims[0] * dims[1] * dims[2]

    if verbose == True:
        print(f"Rank: {rank}")
        print(f"dims: {dims}")
        print(f"spacing: {spacing}")
        print(f"data_dtype: {data_dtype}")
        print(f"split_sizes: {split_sizes}")
        print(f"split_sizes_input: {split_sizes_input}")
        print(f"disp_input: {disp_input}")
        print(f"length: {length}")
        print(flush=True)

    # Scattering the data
    if rank == 0:
        print("Scattering the data...", flush=True)
    
    recvbuf = np.zeros(( int(split_sizes[rank]) , dims[1], dims[2]), order='C', dtype='float64')

    if verbose == True:
        if rank == 0:
            print(f"data.dtype: {data.dtype}, data.shape: {data.shape}, data.size: {data.size}")
            print(flush=True)
        print("Rank:", rank)
        print(f"recvbuf.dtype: {recvbuf.dtype}, recvbuf.shape: {recvbuf.shape}, recvbuf.size: {recvbuf.size}")
        print(flush=True)

    comm.Barrier()
    comm.Scatterv([data, split_sizes_input, disp_input, MPI.DOUBLE], recvbuf, root=0)

    if (track_time == True) and (rank == 0):
        scatter_time = MPI.Wtime()
    
    if rank == 0:
        print("Scattered the data")
        print(flush=True)

    if verbose == True:
        print(f"Rank: {rank}")
        print("Shape of scattered data:", recvbuf.shape)
        print(flush=True)
    # comm.Scatterv(data, recvbuf, root=0)

    # Simple random sampling
    recvbuf = simple_rs(recvbuf, p)

    # Get coordinates values of sampled data
    coord_disps = np.insert(np.cumsum(split_sizes), 0, 0)[0: -1] * spacing[0]
    coords, vals = get_coords_and_vals(recvbuf, spacing, data_dtype)
    coords[:, 0] = coords[:, 0] + coord_disps[rank]

    if verbose == True:
        print(f"Rank: {rank}")
        print(f"Starting x-coordinates: {coord_disps[rank]}")
        print(flush=True)
    
    if (track_time == True) and (rank == 0):
        comp_time = MPI.Wtime()

    # Define input buffer for sampled coordinates and values
    if rank == 0:
        all_point_counts = np.zeros(size, order='C', dtype='int')
    else:
        all_point_counts = None

    point_counts = np.zeros(size, order='C', dtype='int')
    point_counts[rank] = coords.shape[0]

    comm.Reduce(point_counts, all_point_counts, root=0, op=MPI.SUM)

    if rank == 0:
        all_coord_counts = all_point_counts * 3

        coord_buf_disps = np.insert(np.cumsum(all_coord_counts), 0, 0)[0:-1]
        val_buf_disps = np.insert(np.cumsum(all_point_counts), 0, 0)[0:-1]

        if verbose == True:
            print("Size of points in each node:")
            print(all_point_counts)
            print("Size of coordinates array in each node:")
            print(all_coord_counts)
            print("Memory displacements of values array:")
            print(val_buf_disps)
            print("Memory displacements of coordinates array:")
            print(coord_buf_disps)
            print(flush=True)

        final_coords = np.empty((np.sum(all_point_counts), 3), order='C', dtype='float32')
        final_vals = np.empty(np.sum(all_point_counts), order='C', dtype='float64')
    else:
        all_coord_counts = None
        coord_buf_disps = None
        val_buf_disps = None

        final_coords = None
        final_vals = None

    all_point_counts = comm.bcast(all_point_counts, root=0)
    all_coord_counts = comm.bcast(all_coord_counts, root=0)
    coord_buf_disps = comm.bcast(coord_buf_disps, root=0)
    val_buf_disps = comm.bcast(val_buf_disps, root=0)

    # Gathering the point data
    if verbose == True:
        print(f"Rank: {rank}")
        print(f"coords.shape: {coords.shape}, coords.size: {coords.size}, coords.dtype: {coords.dtype}")
        print(f"vals.shape: {vals.shape}, vals.size: {vals.size}, vals.dtype: {vals.dtype}")
        print(flush=True)

    comm.Barrier()

    comm.Gatherv(coords, [final_coords, all_coord_counts, coord_buf_disps, MPI.FLOAT], root=0)
    comm.Gatherv(vals, [final_vals, all_point_counts, val_buf_disps, MPI.DOUBLE], root=0)

    if (track_time == True) and (rank == 0):
        gather_time = MPI.Wtime()

    if rank == 0:
        print("Gathered sampled data")
        print("Shape of coordinates array:", final_coords.shape)
        print("Shape of values array:", final_vals.shape)
        print(flush=True)

        # Saving the output
        print(f"Saving output to {out_file_name}", flush=True)
        save_to_vtp(final_coords, final_vals, out_file_name)
        print(f"Saved to {out_file_name}")
        print(flush=True)

        if (track_time == True) and (rank == 0):
            saving_time = MPI.Wtime()

        # Some sampling information
        sampled_length = final_coords.shape[0]
        print(f"{sampled_length} sampled out of {length} data points. Sampling rate: {sampled_length/length}")
        print(flush=True)

        if track_time == True:
            total_time = saving_time - start_time
            
            saving_time = saving_time - gather_time
            gather_time = gather_time - comp_time
            comp_time = comp_time - scatter_time
            scatter_time = scatter_time - reading_time
            reading_time = reading_time - start_time

            print("reading_time:", reading_time)
            print("scatter_time:", scatter_time)
            print("comp_time:", comp_time)
            print("gather_time:", gather_time)
            print("saving_time:", saving_time)
            print("total_time:", total_time)

            with open("srs_time.csv", 'a') as f:
                f.write(f"{size},{p},{reading_time},{scatter_time},{comp_time},{gather_time},{saving_time},{total_time}\n")


    # # Gathering the data
    # comm.Gatherv(recvbuf, [final_data, split_sizes_input, disp_input, MPI.FLOAT], root=0)

    # if rank == 0:
    #     print("Gathered everything")
    #     test_arr = np.invert( np.isnan(final_data) ).nonzero()
    #     sampled_length = len(test_arr[0])
    #     assert len(test_arr[0]) == len(test_arr[1])
    #     assert len(test_arr[1]) == len(test_arr[2])

    #     # Checking if the samples points and locations are same as in original array
    #     sampled_length = len(test_arr[0])
        
    #     print(f"{sampled_length} sampled out of {length} data points. Sampling rate: {sampled_length/length}")

    #     out_arr = final_data[ test_arr ] - data[ test_arr ]
    #     print("0 value of next 2 outputs indicates that sampled values are equal to original values:", np.min(out_arr), np.max(out_arr))

if __name__ == '__main__':
    usage = "usage: %prog [options] in_file"
    parser = OptionParser(usage=usage)
    
    parser.add_option("-r", "--sampling-ratio", dest="prob", type="float", default="0.001",
        help="sampling ratio between 0 and 1 [default: %default]", metavar="FLOAT")
    
    parser.add_option("-o", "--out-file", dest="out_file", type="string", default="out_srs.vtp",
        help="name of output vtp file [default: %default]", metavar="FILE_NAME")
    
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,
        help="detailed log")
    
    parser.add_option("-t", "--track-time", dest="track_time", action="store_true", default=False,
        help="Append to srs_time.csv in format: proc_num,reading_time,scatter_time,comp_time,gather_time,saving_time,total_time")
    
    options, args = parser.parse_args()
    prob = options.prob
    out_file = options.out_file
    verbose = options.verbose
    track_time = options.track_time
    in_file = args[0]

    assert (0 < prob) and (prob < 1)
    if ( len(out_file) <= 4 ) or out_file[-4:] != ".vtp":
        out_file = out_file + ".vtp"
    
    if verbose==True and rank == 0:
        print("Arguments:")
        print("prob:", prob)
        print("out_file:", out_file)
        print("in_file:", in_file)
        print("verbose:", verbose)
        print("track_time:", track_time)
        print(flush=True)

    main(in_file, p=options.prob, out_file_name=out_file, verbose=verbose, track_time=track_time)

MPI.Finalize()
