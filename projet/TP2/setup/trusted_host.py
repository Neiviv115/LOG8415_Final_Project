from database import SQLConnect
from sshtunnel import SSHTunnelForwarder
import os
import sys

class TrustedHost:
    """Proxy pattern implementation used to route requests to the MySQL cluster."""
    def __init__(self, private_key, gatekeeper_private_dns):
        """
        Initializes a TrustedHost instance.

        Parameters:
        - private_key (str): The path to the private key file.
        - gatekeeper_private_dns (str): The private DNS of the Gatekeeper.
        """
        self.private_key = private_key
        self.gatekeeper_private_dns = gatekeeper_private_dns

    def forward_request(self, target_host, query, target_private_dns):
        """SSH Tunnel for forwarding requests to the MySQL cluster.

        Parameters:
        - target_host (str): The target host information.
        - query (str): The SQL query to be executed.
        - target_private_dns (str): The private DNS of the target host.
        """
        with SSHTunnelForwarder(target_host, ssh_username="ubuntu", ssh_pkey=self.private_key, remote_bind_address=(target_private_dns, 3306)):
            SQLConnect(target_private_dns).execute_query(query)

    def forward(self, query, target_private_dns=''):
        """Forwards SQL queries to the MySQL cluster.

        Parameters:
        - query (str): The SQL query to be executed.
        - target_private_dns (str): The private DNS of the target host (default is an empty string).
        """
        if target_private_dns:
            self.forward_request(target_host=target_private_dns, query=query, target_private_dns=self.gatekeeper_private_dns)
        else:
            self.forward_request(target_host=self.gatekeeper_private_dns, query=query, target_private_dns=target_private_dns)

if __name__ == "__main__":
    # Get environment variables
    private_key = os.getenv('KEYPAIR')
    gatekeeper_private_dns = os.getenv('PROXY_DNS')

    # Check if target_private_dns is provided as a command line argument
    if len(sys.argv) == 2:
        target_private_dns = sys.argv[1]

        # Create TrustedHost instance
        trusted_host = TrustedHost(private_key, gatekeeper_private_dns)

        # Forward the query to the MySQL cluster
        query = "Your SQL Query Here"
        trusted_host.forward(query, target_private_dns)

        
    