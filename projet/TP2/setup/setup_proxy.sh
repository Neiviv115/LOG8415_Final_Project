
# Setting env variables to be used by proxy
echo export KEYPAIR=$1 | sudo tee -a /etc/environment
echo export MANAGER_PRIVATE_DNS=$2 | sudo tee -a /etc/environment
echo export NODE1_PRIVATE_DNS=$3 | sudo tee -a /etc/environment
echo export NODE2_PRIVATE_DNS=$4 | sudo tee -a /etc/environment
echo export NODE3_PRIVATE_DNS=$5 | sudo tee -a /etc/environment

sudo apt update

# Install pip
sudo apt install -y python3-pip

# Install necessary packages
sudo pip install paramiko sshtunnel pymysql pythonping