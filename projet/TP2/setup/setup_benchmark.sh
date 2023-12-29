# Fetch sakila sql files
sudo wget https://downloads.mysql.com/docs/sakila-db.tar.gz;
sudo tar -xf sakila-db.tar.gz;

# Create sakila database and populate tables
sudo mysql -e "SOURCE /home/user/sakila-db/sakila-schema.sql;";
sudo mysql -e "SOURCE /home/user/sakila-db/sakila-data.sql;";

### BENCHMARKING ###
sudo apt-get install -y sysbench

# Create test table sbtest1
sudo sysbench \
oltp_insert \
--table-size=100000 \
--mysql-db=sakila \
--mysql-user=root \
prepare

# Run benchmarking
sudo sysbench \
oltp_read_write \
--table-size=100000 \
--db-driver=mysql \
--mysql-db=sakila \
--mysql-user=root \
--time=60 \
--max-requests=0 \
--threads=6 \
run > benchmark_results.txt

# Clean up test table sbtest1
sudo sysbench \
oltp_read_write \
--mysql-db=sakila \
--mysql-user=root \
cleanup