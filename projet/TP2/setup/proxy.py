from database import DBConnector
from sshtunnel import SSHTunnelForwarder
from pythonping import ping

import random
import os
import sys

class Proxy:
    """Proxy pattern implementation used to route requests to MySQL cluster."""
    def __init__(self, private_key_path, manager_dns, node1_dns, node2_dns, node3_dns):
        """Constructor

        Parameters
        ----------
        private_key_path : string
            File path of private key used to SSH into EC2 instances.
        manager_dns : string
            Private DNS of cluster manager
        node1_dns : string
            Private DNS of the first cluster data node
        node2_dns : string
            Private DNS of the second cluster data node
        node3_dns : string
            Private DNS of the third cluster data node
        """
        self.private_key_path = private_key_path
        self.manager_dns = manager_dns
        self.node1_dns = node1_dns
        self.node2_dns = node2_dns
        self.node3_dns = node3_dns

    def forward_request(self, target_host, query):
        """Start SSH tunnel into the target host to execute the request.

        Parameters
        ----------
        target_host : string
            Service where the tunnel connection is made
        query : string
            Query to be executed
        """
        with SSHTunnelForwarder(
            target_host, ssh_username="user", ssh_pkey=self.private_key_path, remote_bind_address=(self.manager_dns, 3306)
        ) as tunnel:
            DBConnector(self.manager_dns).execute_query(query)

    def direct_hit(self, query):
        """Forward request directly to the cluster manager instance.

        Parameters
        ----------
        query : string
            Query to be executed
        """
        print(f"Chosen node: {self.manager_dns}")
        self.forward_request(self.manager_dns, query)

    def random_hit(self, query):
        """Forward request to a random data node.

        Parameters
        ----------
        query : string
            Query to be executed
        """
        # Choose randomly a data node
        target_host = random.choice([self.node1_dns, self.node2_dns, self.node3_dns])
        print(f"Chosen node: {target_host}")
        self.forward_request(target_host, query)

    def ping_server(self, server_dns):
        """Retrieve average response time of the server after ping.

        Parameters
        ----------
        server_dns : string
            Private DNS of the server
        """
        return ping(target=server_dns, count=1, timeout=2).rtt_avg_ms

    def custom_hit(self, query):
        """Forward request to the data node with the lowest ping response time.

        Parameters
        ----------
        query : string
            Query to be executed
        """
        nodes = [self.node1_dns, self.node2_dns, self.node3_dns]
        avg_latencies = [self.ping_server(host) for host in nodes]

        # Custom: Measure ping for all servers and choose the one with the lowest response time
        fastest_node = nodes[avg_latencies.index(min(avg_latencies))]
        print(f"Chosen node: {fastest_node}")
        self.forward_request(fastest_node, query)

if __name__ == "__main__":

    # Get environment variables
    private_key_path = os.getenv('KEYPAIR')
    manager_dns = os.getenv('MANAGER_PRIVATE_DNS')
    node1_dns = os.getenv('NODE1_PRIVATE_DNS')
    node2_dns = os.getenv('NODE2_PRIVATE_DNS')
    node3_dns = os.getenv('NODE3_PRIVATE_DNS')

    # Get the passed request
    request = sys.argv[1]

    proxy = Proxy(private_key_path, manager_dns, node1_dns, node2_dns, node3_dns)

    print("DIRECT HIT:")
    proxy.direct_hit(request)

    print("RANDOM:")
    proxy.random_hit(request)

    print("LOWEST RESPONSE TIME:")
    proxy.custom_hit(request)
