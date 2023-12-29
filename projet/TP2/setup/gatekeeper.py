from database import SQLConnect
from sshtunnel import SSHTunnelForwarder
import os
import sys

class GateKeeper:
    """Proxy pattern implementation used to route requests to the MySQL cluster."""
    def __init__(self, private_key, trusted_host_private_dns):
        """
        Initializes a GateKeeper instance.

        Parameters:
        - private_key (str): The path to the private key file.
        - trusted_host_private_dns (str): The private DNS of the trusted host.
        """
        self.private_key = private_key
        self.trusted_host_private_dns = trusted_host_private_dns

    def forward_request(self, target_host, query):
        """SSH Tunnel for forwarding requests to the MySQL cluster.

        Parameters:
        - target_host (tuple): The target host information.
        - query (str): The SQL query to be executed.
        """
        with SSHTunnelForwarder(target_host, ssh_username="ubuntu", ssh_pkey=self.private_key, remote_bind_address=(self.trusted_host_private_dns, 3306)):
            SQLConnect(self.trusted_host_private_dns).execute_query(query)

    def forward(self, query):
        """Forwards SQL queries to the MySQL cluster.

        Parameters:
        - query (str): The SQL query to be executed.
        """
        self.forward_request(target_host=self.trusted_host_private_dns, query=query)

if __name__ == "__main__":
    # Get environment variables
    private_key = os.getenv('KEYPAIR')
    th_private_dns = os.getenv('TRUSTED_HOST_DNS')

    # Check if the correct number of command line arguments is provided
    if len(sys.argv) == 2:
        query = sys.argv[1]

        # Create GateKeeper instance
        gatekeeper = GateKeeper(private_key, th_private_dns)

        # Forward the query to the MySQL cluster
        gatekeeper.forward(query)

        
   