import boto3
import time
from remote import Remote


def get_key_pair(ec2_client, key_name):
    """
    Get an existing EC2 key pair by name.

    Parameters:
    - ec2_client: Boto3 EC2 client.
    - key_name: Name of the key pair to retrieve.

    Returns:
    - Key pair information if it exists, None otherwise.
    """
    try:
        response = ec2_client.describe_key_pairs(KeyNames=[key_name])
        key_pairs = response.get('KeyPairs', [])
        
        if key_pairs:
            # Key pair with the specified name already exists, return it
            return key_pairs[0]
        else:
            return None
    except Exception as e:
        print(f"An error occurred while retrieving the key pair: {e}")
        return None


def create_key_pair(ec2_client, key_name):
    """
    Create an EC2 key pair if it doesn't exist, or retrieve an existing one.

    Parameters:
    - ec2_client: Boto3 EC2 client.
    - key_name: Name for the key pair.

    Returns:
    - Key pair information.
    """
    existing_key_pair = get_key_pair(ec2_client, key_name)
    if existing_key_pair:
        print(f"Key pair '{key_name}' already exists.")
        return existing_key_pair
    # Key pair doesn't exist; create a new one
    try:
        response = ec2_client.create_key_pair(KeyName=key_name)
        key_pair = response['KeyMaterial']
        # Save the key pair to a pem file
        with open(f'{key_name}.pem', 'w') as key_file:
            key_file.write(key_pair)
        return key_pair
    except Exception as e:
        print(f"An error occurred while creating the key pair: {e}")
        return None


def create_security_group(client, name, description="Default TP1 security group"):
    """
    Create a security group and returns its id

    Parameters
    ----------
    client :
        The ec2 client
    name : string
        Name of the security group
    description : string, optional
        Description of the security group

     Returns
    -------
    id : int
        The security group id
    """
    try : 
        response = client.create_security_group(GroupName=name, Description=description)
        # Define SSH (port 22) and HTTP (port 80) inbound rules + port 5000 (used for flask)
        id = response["GroupId"]
        client.authorize_security_group_ingress(
            GroupId=id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                },
                { # We also add the port 5000 to our rules because we will deploy the flask app in user mode on this port 
                # (80 is a privileged port)
                    'IpProtocol': 'tcp',
                    'FromPort': 5000,
                    'ToPort': 5000,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}], # for all IP adresses
                },
            ],
        )
        return id
    except Exception as e:
        print(f"An error occurred while creating the security group: {e}")
        return None


def create_one_instance(ec2_ressource, ami_id, instance_type, security_group_id, subnet_id, key_name):
    """
    Create one instance of instance_type linked to a security group in a specific subnet

    Parameters
    ----------
    ec2_ressource : 
        The reference to the session ec2 ressource
    ami_id : string
        Amazon Machine ID, can be found in the learner lab when you create an instance (right pannel)
    instance_type : string
        Either m4.large or t2.large for this TP
    security_group_id : int
        Identifier of the security group for these instances
    subnet_id : string
        The identifier of the subnet where we create the instance
    key_name : string
        The name of a key_pair registered in ec2, so you can connect through ssh 
    
     Returns
    -------
    id : int
        The identifier of the instance created
    """    
    try:
        instance = ec2_ressource.create_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[security_group_id],
            SubnetId=subnet_id,
            KeyName=key_name,
        )
        return instance[0].id
    except Exception as e:
        print(f"An error occurred while creating the instance: {e}")
        return None


def create_ec2_instances(ec2_ressource, ami_id, instance_type, security_group_id, subnets_list, key_name, number=1):
    """
    Create a certain number of instances of one instance_type linked to a security group

    Parameters
    ----------
    ec2_ressource : 
        The reference to the session ec2 ressource
    ami_id : string
        Amazon Machine ID, can be found in the learner lab when you create an instance (right pannel)
    instance_type : string
        Either m4.large or t2.large for this TP
    security_group_id : int
        Identifier of the security group for these instances
    subnets_list : subnet[]
        The list of subnets to use for this group of instances
    key_name : string
        The name of a key_pair registered in ec2, so you can connect through ssh 
    number : int
        Number of instances to create
    
     Returns
    -------
    id_array : int
        The identifiers of all the instances created
    """
    # We create the instances on different subnets so they will be on different availability zones
    # (at least for us with our student account and the subnets already available)
    id_array = [create_one_instance(ec2_ressource, ami_id, instance_type, security_group_id, 
                                    subnets_list[i%len(subnets_list)]['SubnetId'], 
                                    key_name) for i in range(number)]
    return id_array


def get_public_dns(ec2_client, instance_id):
    """
    Returns the public DNS associated with the instance whose id is instance_id.
    The instance needs to be in a running state.

    Parameters:
    - ec2_client: Boto3 EC2 client.
    - instance_id: Identifier of the instance.

    Returns:
    - The public DNS name of the instance that can be use to connect through SSH
    """
    # Wait for the instance to be in the 'running' state
    while True:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        state = response['Reservations'][0]['Instances'][0]['State']['Name']
        if state == 'running':
            break
    public_dns = response['Reservations'][0]['Instances'][0].get('PublicDnsName')
    return public_dns

def get_private_dns(ec2_client, instance_id):
    # Wait for the instance to be in the 'running' state
    while True:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        state = response['Reservations'][0]['Instances'][0]['State']['Name']
        if state == 'running':
            break
    private_dns = response['Reservations'][0]['Instances'][0].get('PrivateDnsName')
    return private_dns


def delete_security_group_by_name(ec2_client, group_name):
    """
    Delete a security named 'group_name'.

    Parameters:
    - ec2_client: Boto3 EC2 client.
    - group_name: Name of the security group to delete.

    Returns:
    - True if the security group was deleted, False otherwise.
    """
    try:
        # Get the security group details by name
        response = ec2_client.describe_security_groups(GroupNames=[group_name])
        if not response['SecurityGroups']: # Security group not found
            return False 

        # Get the security groups ID and delete the associated instances
        security_group_id = response['SecurityGroups'][0]['GroupId']
        terminated_instance_ids = delete_instances_by_security_group(ec2_client, security_group_id)

        # It takes some time for ec2 to effectively delete the instances, we have to wait
        if terminated_instance_ids:
            print(f"Waiting for instances to be terminated: {', '.join(terminated_instance_ids)}")
            ec2_client.get_waiter('instance_terminated').wait(InstanceIds=terminated_instance_ids)

        time.sleep(5) # Gives some free time to notify the security group that the instances have been deleted
        # Delete the security group
        ec2_client.delete_security_group(GroupName=group_name)

        if terminated_instance_ids:
            print(f"Terminated associated instances: {', '.join(terminated_instance_ids)}")
        return True
    
    except Exception as e:
        if e.response['Error']['Code'] == 'InvalidGroup.NotFound': # Normal if there is no target group, can ignore
            return
        else:
            print(f"An error occurred while deleting the security group: {e}")
    

def delete_instances_by_security_group(ec2_client, security_group_id):
    """
    Delete instances associated with a specific security group.

    Parameters:
    - ec2_client: Boto3 EC2 client.
    - security_group_id: Identifier of the security group.

    Returns:
    - List of instance IDs that were terminated.
    """
    terminated_instance_ids = []

    try:
        # Get instances associated with the security group
        instances = ec2_client.describe_instances(
            Filters=[
                {'Name': 'instance.group-id', 'Values': [security_group_id]},
                {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
            ]
        )

        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                # Terminate each instance
                ec2_client.terminate_instances(InstanceIds=[instance_id])
                terminated_instance_ids.append(instance_id)
        return terminated_instance_ids
    
    except Exception as e:
        print(f"An error occurred while terminating instances: {e}")
        return []
    

def wait_instances_to_run(ec2_client, instance_ids):
    # Create an EC2 waiter for instances to be running
    print("Waiting for", instance_ids, "to be running")
    instance_waiter = ec2_client.get_waiter('instance_running')

    # Wait for instances to be in the running state
    instance_waiter.wait(InstanceIds=instance_ids)
    time.sleep(2)


def setup_node(private_keyfile, node_public_dns,node_id):
    """Setup data node remotely using RemoteClient object
        
        Parameters
        ----------
        private_keyfile :   string
                            File path of private key
        node_public_dns :   string
                            Public DNS of cluster data node 
        node_id :           int
                            ID of node (1,2,3)
        """

    node_client = Remote(hostname=node_public_dns, usrname="ubuntu", private_keyfile=private_keyfile)

    node_client.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\setup\setup_cluster_node.sh', remote_path='/home/ubuntu/setup_cluster_node.sh')
    node_client.upload_file(local_path=r'C:\Users\meyri\CloudComp\projet\TP2\configs\my.cnf', remote_path='/home/ubuntu/my.cnf')

    node_client.exec("sh setup_cluster_node.sh")

    node_client.close_connection()