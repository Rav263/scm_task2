#! /bin/bash
echo "./run_exp.sh <from> <to runs> <eps> <cpus>"

eps=${3}

for cpu in 1 4 8 16 32
do
    for run in $(seq $1 1 $2)
    do
        if ((${cpu} == 32)); then
	        echo "mpirun --use-hwthread-cpus -n ${cpu} main ${eps} > results/home_pc/res_${eps}_${cpu}_run_${run}"
	        mpirun --use-hwthread-cpus -n ${cpu} main ${eps} > results/home_pc/res_${eps}_${cpu}_run_${run}
        else
	        echo "mpirun -n ${cpu} main ${eps} > results/home_pc/res_${eps}_${cpu}_run_${run}"
	        mpirun -n ${cpu} main ${eps} > results/home_pc/res_${eps}_${cpu}_run_${run}
        fi
    done
done
