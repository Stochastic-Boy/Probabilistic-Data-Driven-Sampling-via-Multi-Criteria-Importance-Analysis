#!/bin/bash
# while [ True ]; do
#     if [ "$1" = "--create-hostfile" -o "$1" = "-c" ]; then
#         ./pingServers.sh 172.27.19.1 172.27.19.20 > hostfile.txt
#         shift 1
#     else
#         break
#     fi
# done

# mpirun -np 64 --hostfile hostfile.txt python3 gbs.py -t -r 0.1 -b 32 -o Isabel_vbs Isabel_Pressure_Large.vti 

for samp in 0.01 0.02 0.03 0.04 0.05
do
    echo $samp
    mpirun -np 8 --hostfile hostfile.txt python3 gbs.py -b 16 -r $samp -o Isabel_gbs_$samp Isabel_Pressure_Large.vti
done
