import paramiko
from scp import SCPClient
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    instances_ids = []
    instances_dns_names = []
    with open("instances_info.txt", 'r') as var_file:            
            lines = var_file.readlines()
            for line in lines[:7]:
                line = line.strip().split(' ')
                instances_ids.append(line[0])
                instances_dns_names.append(line[1])
    
    dns = instances_dns_names[0]
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(dns, username="ec2-user", key_filename="my_key_pair.pem")

    files_to_retrieve = ['comparison_linux.csv', 'comparison_spark.csv']

    # Loop through the files and download them
    for file_name in files_to_retrieve:
        remote_file_path = file_name
        local_file_path = f"comparisons/{file_name}"

        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_file_path, local_path=local_file_path)

    # Close the SSH connection
    ssh.close()

    # Treat the results
    # First dataframe: Linux/Hadoop comparison
    df1 = pd.read_csv("comparisons/comparison_linux.csv")
    df1_linux = df1[df1["method"]=="linux"]
    df1_hadoop = df1[df1["method"]=="hadoop"]
    print("Statistics for 10 wordcounts with Linux commands:")
    print("Mean time:", np.mean(df1_linux["time"])," milliseconds.")
    print("Standard variance:", np.std(df1_linux["time"]))
    print("Statistics for 10 wordcounts with Hadoop MapReduce:")
    print("Mean time:", np.mean(df1_hadoop["time"])," milliseconds.")
    print("Standard variance:", np.std(df1_hadoop["time"]))

    # Second dataset: Spark / Hadoop comparison
    df2 = pd.read_csv("comparisons/comparison_spark.csv")
    average_times = df2.groupby(['file', 'method'])['time'].mean().unstack()

    # Create a bar chart and saves it
    ax = average_times.plot(kind='bar', stacked=False, figsize=(10, 6))
    ax.set_ylabel('Average Time in seconds')
    ax.set_xlabel('File')
    ax.set_title("Time taken to use wordcount for each file, \nwith Hadoop or Spark")
    plt.xticks(rotation = -45)
    plt.legend(title='Method', loc='upper left', bbox_to_anchor=(1, 1))
    plt.savefig("comparisons/barplot.png", bbox_inches='tight')