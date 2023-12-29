# Set environment variables for proxy.py
echo export KEYPAIR=$1 | sudo tee -a /etc/environment
echo export GATEKEEPER=$2 | sudo tee -a /etc/environment

sudo apt update
sudo apt install -y python3-pip
sudo pip install paramiko sshtunnel pymysql pythonping