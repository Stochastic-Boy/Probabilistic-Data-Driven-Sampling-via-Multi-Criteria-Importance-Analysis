# Parallel-Probabilistic-Data-Sampling Algorithms
Implementing MPI-based parallel data sampling methods based on the following paper: [https://ieeexplore.ieee.org/document/9130956](url)

The code implemented here runs on MPI with nodes accessible via passwordless ssh. The input is assumed to be VTK image file with 3 dimensions, and the sampled point cloud is stored in the VTP format.

## How to run

The steps to run the project parallelly are as follows:

Step 1: Download the files in the `src` file from the GitHub repository in your working directory. Also, have the data files in the working directory.

Step 2: Upload the files into the remote workspace using ```sftp``` (Simple File Transfer Protocol)

Step 3: Open the terminal/Powershell in your system and run ```ssh 172.27.19._``` where _ is any number from 1 to 60  to access the KD lab system (generally ```ssh <to-the-computing-node>```)

Step 4: Create a `hostfile.txt`. It contains the IP addresses of the computing nodes and the number of processes to be run on each node.

Step 5: Run the following statement to run gradient-based sampling on 8 processors, with 16 bins and 0.01 sampling rate. The output file will be saved to `Isabel_gbs_0.01.vtp`.
```
mpirun -np 8 --hostfile hostfile.txt python3 gbs.py -b 16 -r 0.01 -o Isabel_gbs_0.01 Isabel_Pressure_Large.vti
```

Step 6: Use `sftp` to get the sampled files to your workspace.

## Commandline Options

The sampling algorithms are implemented in the following files:
- `srs.py`: Simple random sampling
- `vbs.py`: Value-based importance sampling
- `gbs.py`: Smoothness-based importance sampling


`mpirun` is the command which uses MPI to run the code in parallel. We use the following options:
```
Options:
  -np                   shows the processes we are going to run
  --hostfile FILE       file containing IP addresses of the computing nodes
```


Options in the python files (all are common except the bin number)

```
Options:
  -h, --help            show this help message and exit
  -r FLOAT, --sampling-ratio=FLOAT
                        sampling ratio between 0 and 1 [default: 0.001]
  -b INT, --bin-num=INT
                        number of bins [default: 16]
  -o FILE_NAME, --out-file=FILE_NAME
                        name of output vtp file [default: out_gbs.vtp]
  -v, --verbose         detailed log
  -t, --track-time      Append to vbs_time.csv in format: proc_num,bin_num,prob,reading_time,scatter_time,comp_time,gather_time,saving_time,total_time
```

## Miscellaneous

We created some utility shell scripts to ease the process of studying the algorithms, they are in the `misc` folder.

- `pingServers.sh`: Pings all servers in an ip address range and outputs the pingable nodes to stdout with an hardcoded number of processes at each node
- `run.sh`: Some commands to run the main commands.
- `scaling_study.sh`: For loops for multiple runs and storing the time data in csv files.

**NOTE**: These files were used by us and have not been generalised for use.
