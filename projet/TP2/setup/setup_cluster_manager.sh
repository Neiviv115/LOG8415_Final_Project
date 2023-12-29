# Update system
sudo apt update

# Fetch nbd management server DEB package
sudo wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.0/mysql-cluster-community-management-server_8.0.31-1ubuntu22.04_amd64.deb

# Install DEB package
sudo apt install -y ./mysql-cluster-community-management-server_8.0.31-1ubuntu22.04_amd64.deb

### CLUSTER MANAGER CONFIGURATION ###
sudo mkdir /var/lib/mysql-cluster
sudo mv config.ini /var/lib/mysql-cluster/config.ini


# Start the manager
sudo ndb_mgmd -f /var/lib/mysql-cluster/config.ini