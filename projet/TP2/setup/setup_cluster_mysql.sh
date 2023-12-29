
### MYSQL SERVER INSTALLATION ###

# Fetch DEB bundle package
sudo wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.0/mysql-cluster_8.0.31-1ubuntu22.04_amd64.deb-bundle.tar

# Create extract directory
sudo mkdir mysql_packages

# Extract archive 
sudo tar -xvf mysql-cluster_8.0.31-1ubuntu22.04_amd64.deb-bundle.tar -C mysql_packages/

# Install dependencies
sudo apt install -y libaio1 libmecab2

# Install extracted deb packages
sudo apt install -y ./mysql_packages/mysql-common_8.0.31-1ubuntu22.04_amd64.deb
sudo apt install -y ./mysql_packages/mysql-cluster-community-client-plugins_8.0.31-1ubuntu22.04_amd64.deb
sudo apt install -y ./mysql_packages/mysql-cluster-community-client-core_8.0.31-1ubuntu22.04_amd64.deb
sudo apt install -y ./mysql_packages/mysql-cluster-community-client_8.0.31-1ubuntu22.04_amd64.deb
sudo apt install -y ./mysql_packages/mysql-client_8.0.31-1ubuntu22.04_amd64.deb
sudo apt install -y ./mysql_packages/mysql-cluster-community-server-core_8.0.31-1ubuntu22.04_amd64.deb
sudo apt install -y ./mysql_packages/mysql-cluster-community-server_8.0.31-1ubuntu22.04_amd64.deb # Prompt
sudo apt install -y ./mysql_packages/mysql-server_8.0.31-1ubuntu22.04_amd64.deb

sudo mv -f mysql.cnf /etc/mysql/my.cnf

# echo "Restarting mysql service..."
sudo pkill -f ndb_mgmd
sudo ndb_mgmd -f /var/lib/mysql-cluster/config.ini

sudo systemctl restart mysql

echo "Cluster mysql server installation done!"