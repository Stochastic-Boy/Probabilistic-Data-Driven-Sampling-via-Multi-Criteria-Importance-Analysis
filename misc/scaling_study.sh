#!/bin/bash

# for num in 1 2 4 8 16 32 64
# do
#     for samp in 0.01 0.02 0.03 0.04 0.05 0.06 0.07 0.08 0.09 0.1
#     do
#         for (( i=0; i < 10; i++))
#         do
#             echo $num $i $samp
#             mpirun -np $num --hostfile hostfile.txt python3 srs.py -r $samp -t -o Isabel_srs Isabel_Pressure_Large.vti
#         done
#     done
# done

for num in 16
do
    for samp in 0.01 
    do
        for (( i=0; i < 4; i++))
        do
            echo $num $i $samp $bin
            mpirun -np $num --hostfile hostfile.txt python3 vbs.py -r $samp -t -b 32 -o Isabel_srs Isabel_Pressure_Large.vti
        done
    done
done

for num in 32 64
do
    for samp in 0.001 0.01 
    do
        for bin in 1 2 4 8 16
        do
            for (( i=0; i < 3; i++))
            do
                echo $num $i $samp $bin
                mpirun -np $num --hostfile hostfile.txt python3 vbs.py -r $samp -t -b $bin -o Isabel_srs Isabel_Pressure_Large.vti
            done
        done
    done
done


for num in 1 2 4 8 16 32 64
do
    for samp in 0.01
    do
        for bin in 1 2 4 8 16
        do
            for (( i=0; i < 3; i++))
            do
                echo $num $i $samp $bin
                mpirun -np $num --hostfile hostfile.txt python3 gbs.py -r $samp -t -b $bin -o Isabel_srs Isabel_Pressure_Large.vti
            done
        done
    done
done