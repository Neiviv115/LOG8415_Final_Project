import boto3
import utils_create_instances as utils_instances
import paramiko
from scp import SCPClient
import time
from remote import Remote
import threading


if __name__ == "__main__":
    ec2_ressource = boto3.resource("ec2")
    ec2_client = boto3.client('ec2')
    ami_id = "ami-0c7217cdde317cfec" # ami_id for ubuntu

    response_vpcs = ec2_client.describe_vpcs()
    vpc_id = response_vpcs.get('Vpcs', [{}])[0].get('VpcId', '') # we use the default subnet
    # It should already have multiple subnets listed, on different availability zones
    # (at least it is the case for us with our student accounts)
    ec2_client_subnets = ec2_client.describe_subnets()['Subnets']
    
    key_pair_name = "my_key_pair" 
    # Create EC2 key pair
    key_pair = utils_instances.create_key_pair(ec2_client, key_pair_name)

    # We want to delete everything previously created with the same name
    # so we can create them again without any conflict
    # Delete security groups (and associated instances) if they already exist
    for group_name in ["tp2_sg"]:
        deleted = utils_instances.delete_security_group_by_name(ec2_client, group_name)

    # we create 2 security groups, one for each cluster in case we would
    # like different rules for each cluster
    security_group = utils_instances.create_security_group(ec2_client, "tp2_sg")
    security_group_gk =utils_instances.create_security_group(ec2_client,'gatekeeper')
    security_group_th = utils_instances.create_security_group(ec2_client,'trusted_host')

    #create manager instance
    manager_instance_id = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.micro", security_group, ec2_client_subnets, key_pair_name, 1)
    #create workers instances
    worker_instances_id=utils_instances.create_ec2_instances(ec2_ressource,ami_id,"t2.micro", security_group,ec2_client_subnets,key_pair_name,3)

    # We wait for the instances to be running
    utils_instances.wait_instances_to_run(ec2_client, manager_instance_id)
    utils_instances.wait_instances_to_run(ec2_client, worker_instances_id)
    # We get the public dns name
    manager_instance_dns=utils_instances.get_public_dns(ec2_client,manager_instance_id[0])
    manager_private_dns=utils_instances.get_private_dns(ec2_client,manager_instance_id[0])
    worker_instances_dns = [utils_instances.get_public_dns(ec2_client, id) for id in worker_instances_id]
    worker_private_dns = [utils_instances.get_private_dns(ec2_client, id) for id in worker_instances_id]
    #print(instances_dns)

    #create proxy instance
    proxy_instance_id = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.large", security_group, ec2_client_subnets, key_pair_name, 1)
    utils_instances.wait_instances_to_run(ec2_client, proxy_instance_id)
    proxy_instance_dns=utils_instances.get_public_dns(ec2_client,proxy_instance_id[0])
    proxy_private_dns=utils_instances.get_private_dns(ec2_client,proxy_instance_id[0])
    
    #create standalone server
    server_instance = utils_instances.create_ec2_instances(ec2_ressource,ami_id,"t2.micro",security_group,ec2_client_subnets,key_pair_name,1)
    utils_instances.wait_instances_to_run(ec2_client,server_instance)
    server_dns=utils_instances.get_public_dns(ec2_client,server_instance[0])
    server_private_dns=utils_instances.get_private_dns(ec2_client,server_instance[0])

    #create gatekeeper
    gatekeeper_instance = utils_instances.create_ec2_instances(ec2_ressource,ami_id,"t2.large",security_group_gk,ec2_client_subnets,key_pair_name,1)

    #create trusted host
    trusted_host_instance = utils_instances.create_ec2_instances(ec2_ressource,ami_id,"t2_large",security_group_th,ec2_client_subnets,key_pair_name,1)

    gatekeeper_public_dns = utils_instances.get_public_dns(ec2_client,gatekeeper_instance)
    trusted_host_public_dns = utils_instances.get_public_dns(ec2_client,trusted_host_instance)
    gatekeeper_private_dns = utils_instances.get_private_dns(ec2_client,gatekeeper_instance)
    trusted_host_private_dns = utils_instances.get_private_dns(ec2_client,trusted_host_instance)

    
    remote_client=Remote(hostname=server_dns, usrname="ubuntu", private_keyfile=r"C:\Users\meyri\CloudComp\projet\TP2\my_key_pair.pem")
    remote_client.upload_file(remote_path='/home/ubuntu/setup_standalone_mysql.sh', local_path=r"C:\Users\meyri\CloudComp\projet\TP2\setup\setup_standalone_mysql.sh")
    remote_client.upload_file(remote_path='/home/ubuntu/setup_benchmark.sh',local_path=r'C:\Users\meyri\CloudComp\projet\TP2\setup\setup_benchmark.sh')
    remote_client.exec("sh setup_standalone_mysql.sh")


    
    


    manager = Remote(hostname=manager_instance_dns, usrname="ubuntu", private_keyfile=r"C:\Users\meyri\CloudComp\projet\TP2\my_key_pair.pem")
    manager.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\setup\setup_cluster_mysql.sh',remote_path="/home/ubuntu/setup_standalone_mysql.sh")
    manager.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\setup\setup_benchmark.sh',remote_path='/home/ubuntu/setup_benchmark.sh')
    manager.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\setup\setup_cluster_mysql.sh', remote_path='/home/ubuntu/setup_cluster_mysql.sh')
    manager.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\setup\setup_benchmark.sh', remote_path='/home/ubuntu/setup_benchmark.sh')
    manager.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\configs\config.ini', remote_path='/home/ubuntu/config.ini')
    manager.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\configs\mysql.cnf', remote_path='/home/ubuntu/mysql.cnf')
    manager.exec("sh setup_cluster_manager.sh")

    thread_1 = threading.Thread(target=utils_instances.setup_node, args=('my_key_pair.pem', worker_instances_dns[0],1))
    thread_2 = threading.Thread(target=utils_instances.setup_node, args=('my_key_pair.pem',  worker_instances_dns[1], 2))
    thread_3 = threading.Thread(target=utils_instances.setup_node, args=('my_key_pair.pem',  worker_instances_dns[2], 3))

    # Start threads
    thread_1.start()
    thread_2.start()
    thread_3.start()

    # Wait for threads to terminate
    thread_1.join()
    thread_2.join()
    thread_3.join()
    # Execute cluster mysql server manually
    print(f"""the following steps are needed to setup the SQL cluster server:\n\
     Open a new terminal and run the following:\
    ' ssh -i my_key_pair.pem ubuntu@{manager_instance_dns} '\n\
    ' sh setup_cluster_mysql.sh ' """)
    input("Press enter to continue: ")

    

    print(f"""These steps create an SQL user:\n\
    Run ' sudo mysql -e "CREATE USER proxy@'{proxy_private_dns[0]}' IDENTIFIED BY pwd;" '\n\
    Run ' sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO proxy@'{proxy_private_dns}';" ' """)
    input("Press enter to continue: ")
    
    #Benchmark for standalone and cluster
    manager.exec("sh setup_benchmark.sh")
    remote_client.exec("sh setup_benchmark.sh")

    manager.get_file(remote_filepath='benchmark_results.txt', local_filepath=r'C:\Users\meyri\CloudComp\projet\TP2\results\cluster_benchmark_results.txt')
    remote_client.get_file(remote_filepath='benchmark_results.txt',local_filepath=r'C:\Users\meyri\CloudComp\projet\TP2\results\standalone_benchmark.results.txt')
    print("Benchmark completed.")

    proxy_client = Remote(hostname=proxy_instance_dns,usrname="ubuntu",private_keyfile=r"C:\Users\meyri\CloudComp\projet\TP2\my_key_pair.pem")
    proxy_client.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\setup\setup_proxy.sh',remote_path='/home/ubuntu/setup_proxy.sh')
    proxy_client.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\my_key_pair.pem', remote_path=f'/home/ubuntu/{key_pair_name}.pem')
    proxy_client.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\setup\database.py', remote_path='/home/ubuntu/database.py')
    proxy_client.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\setup\proxy.py', remote_path='/home/ubuntu/proxy.py')

    print(f"""The following steps are required to create the proxy:\n\
    Open a new terminal and run the following: \
    ' ssh -i my_key_pair.pem ubuntu@{proxy_instance_dns} '\n\
    ' sh setup_proxy.sh my_key_pair.pem {manager_private_dns} {worker_instances_dns[0]} {worker_instances_dns[1]} {worker_instances_dns[2]} '\n\
    Start proxy by running ' sudo python3 proxy.py "SELECT COUNT(*) FROM actor;" '""")


     # Setup gatekeeper
    gatekeeper_server = Remote(gatekeeper_public_dns[0], "ubuntu", r"C:\Users\meyri\CloudComp\projet\TP2\my_key_pair.pem")
    trustedhost_server = Remote(trusted_host_public_dns[0], "ubuntu",r"C:\Users\meyri\CloudComp\projet\TP2\my_key_pair.pem")

    gatekeeper_server.upload_file(local_filepath=r'C:\Users\meyri\CloudComp\projet\TP2\setup\setup_gatekeeper.sh', remote_filepath='/home/ubuntu/setup_gatekeeper.sh')
    gatekeeper_server.upload_file(local_filepath=r'C:\Users\meyri\CloudComp\projet\TP2\my_key_pair.pem', remote_filepath=f'/home/ubuntu/{key_pair_name}')
    gatekeeper_server.upload_file(local_filepath=r'C:\Users\meyri\CloudComp\projet\TP2\setup\gatekeeper.py', remote_filepath='/home/ubuntu/gatekeeper.py')

    trustedhost_server.upload_file(local_filepath=r'C:\Users\meyri\CloudComp\projet\TP2\setup\trusted_host.sh', remote_filepath='/home/ubuntu/trusted_host.sh')
    trustedhost_server.upload_file(local_filepath=r'C:\Users\meyri\CloudComp\projet\TP2\my_key_pair.pem', remote_filepath=f'/home/ubuntu/{key_pair_name}')
    trustedhost_server.upload_file(local_filepath=r'C:\Users\meyri\CloudComp\projet\TP2\setup\trusted_host.py', remote_filepath='/home/ubuntu/trusted_host.py')

    print(f"Follow the next steps to setup the gatekeeper correctly\n\
        Open a new terminal and run the following commands:\n\
            ssh -i 'my_key_pair.pem' ubuntu@{gatekeeper_public_dns[0]}\n\
            sh setup_gatekeeper.sh 'my_key_pair.pem' {trusted_host_private_dns[0]} \n\n\
        Open an other new terminal and run the following commands:\n\
            ssh -i 'my_key_pair.pem' ubuntu@{trusted_host_public_dns[0]}\n\
            sh setup_trusted_host.sh 'my_key_pair.pem' {gatekeeper_private_dns[0]}\n\n\
        Now both Gatekeeper and Trusted Host should be running fine.\n")
    
    input("\nIf previous commands run correctly, you can press a key to continue")

