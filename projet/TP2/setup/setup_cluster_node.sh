# Install dependency
sudo apt update
sudo apt install libclass-methodmaker-perl

# Fetch nbd data note DEB package
sudo wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.0/mysql-cluster-community-data-node_8.0.31-1ubuntu22.04_amd64.deb

# Install DEB package
sudo apt install ./mysql-cluster-community-data-node_8.0.31-1ubuntu22.04_amd64.deb

# Move config file
sudo mv -f my.cnf /etc/my.cnf

# Create data directory
sudo mkdir -p /usr/local/mysql/data

# Start data node
sudo ndbd