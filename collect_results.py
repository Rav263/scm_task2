import numpy as np
import pandas as pd

cpus = [1, 4, 8, 16, 32, 60]
eps = ["1.5e-6", "5.0e-6", "3.0e-5"]
runs = [1, 2, 3, 4, 5]

def read_file(cpu, eps, run):
    file_name = f"results/polus/res_{eps}_{cpu}_run_{run}"
    f = open(file_name)
    for line_number, line in enumerate(f):
        words = line.strip().split()
        if ("Solution" in words):
            error = float(words[-1])
            #print(words)
        if ("Compute" in words):
            solution = float(words[-1])
            #print(words)
        if ("Points" in words):
            points = int(words[-1])
            #print(words)
        if ("elapsed:" in words and "Time" in words):
            time = float(words[-1][:-4])
        if ("elap:" in words):
            time_per_point = float(words[-1][:-4])
    return (error, solution, points, time, time_per_point)


per_eps_data = {}

for ep in eps:
    pc_err_mean = []
    pc_sol_mean = []
    pc_poi_mean = []
    pc_tim_mean = []
    pc_tpp_mean = []
    pc_err_std = []
    pc_sol_std = []
    pc_poi_std = []
    pc_tim_std = []
    pc_tpp_std = []
    for cpu in cpus:
        result = []
        for run in runs:
            result.append(read_file(cpu, ep, run))

        df = pd.DataFrame(result)
        df = df.transpose()
        res_mean = [*df.mean(axis=1)]
        res_std = [*df.std(axis=1)]
        
        pc_err_mean.append(res_mean[0])
        pc_sol_mean.append(res_mean[1])
        pc_poi_mean.append(res_mean[2])
        pc_tim_mean.append(res_mean[3])
        pc_tpp_mean.append(res_mean[4])
        pc_err_std.append(res_std[0])
        pc_sol_std.append(res_std[1])
        pc_poi_std.append(res_std[2])
        pc_tim_std.append(res_std[3])
        pc_tpp_std.append(res_std[4])       

    df_err = pd.DataFrame({"cpus": cpus, "mean_err": pc_err_mean, "std_err":pc_err_std})
    df_err = df_err.set_index("cpus")
    df_time = pd.DataFrame({"cpus": cpus, "mean_time": pc_tim_mean, "std_time":pc_tim_std})
    df_time = df_time.set_index("cpus")
    df_time_pp = pd.DataFrame({"cpus": cpus, "mean_time_pp": pc_tpp_mean, "std_time_pp":pc_tpp_std})
    df_time_pp = df_time_pp.set_index("cpus")
    df_points = pd.DataFrame({"cpus": cpus, "mean_points": pc_poi_mean, "std_points":pc_poi_std})
    df_points = df_points.set_index("cpus")
    per_eps_data[ep] = pd.concat([df_err, df_time, df_time_pp, df_points], axis = 1)

#print(per_eps_data)

import matplotlib.pyplot as plt


for now_eps in per_eps_data:
    value = per_eps_data[now_eps]

    plt.xticks(ticks=[*range(len(value.index))], labels=value.index)
    plt.errorbar([*range(len(value.index))], value["mean_time"], 
                 #yerr=value["std_time_pp"], 
                 linestyle='-',marker=".", 
                 capsize=4, label = f"eps={now_eps}")
    
    plt.grid ()
    plt.xlabel ('Количество процессов')
    plt.ylabel ('Среднее время на вычисление')
    plt.legend (loc = 'best')
    plt.savefig(f"{now_eps}_time.pdf")
    plt.clf()


