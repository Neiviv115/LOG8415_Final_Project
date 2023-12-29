import pymysql

class DBConnector:
    """Database connector used to connect the application to the MySQL database."""
    def __init__(self, manager_dns):
        """Constructor

        Parameters
        ----------
        manager_dns : string
            Private DNS of the manager
        """
        self.connection = self.create_connection(manager_dns)

    def create_connection(self, host):
        """Create a connection to the MySQL database.

        Parameters
        ----------
        host : string
            The host where the database server is located

        Returns
        -------
        connection : created database connection
        """
        # Connect to the database
        connection = pymysql.connect(
            host=host,
            port=3306,
            user="proxy",
            password="pwd",
            database='sakila',
            autocommit=True
        )

        return connection

    def execute_query(self, query):
        """Execute an SQL query using the database connection cursor.

        Parameters
        ----------
        query : string
            Query to be executed
        """
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                print(cursor.fetchall())
