import paramiko
from scp import SCPClient
import time


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

    with SCPClient(ssh.get_transport()) as scp:
        scp.put("comparisons/hadoop_spark_comparison.sh", remote_path='hadoop_spark_comparison.sh')

    command = f'chmod 777 hadoop_spark_comparison.sh'
    stdin, stdout, stderr = ssh.exec_command(command)
    command = f'./hadoop_spark_comparison.sh'
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()