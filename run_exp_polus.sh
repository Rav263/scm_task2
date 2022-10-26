#! /bin/bash
echo "./run_exp.sh <from> <to runs> <eps> <cpus>"

eps=${3}
cpu=${4}

for run in $(seq $1 1 $2)
do
	echo "mpisubmit.pl -p ${cpu} -w 00:10 --stdout results_ibm_task_2/res_${eps}_${cpu}_run_${run} main_ibm ${eps}"
	mpisubmit.pl -p ${cpu} -w 00:10 --stdout results_ibm_task_2/res_${eps}_${cpu}_run_${run} main_ibm ${eps}
done
