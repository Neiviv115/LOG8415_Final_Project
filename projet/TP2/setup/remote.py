import paramiko
import time

class Remote:
    """A class for managing remote connections and file transfer using the Paramiko library."""

    def __init__(self, hostname, usrname, private_keyfile):
        """Constructor
        
        Parameters
        -----------
        hostname: string
            the public dns of the host instance
        usrname: string
            the username used
        private_keyfile: string
            the path to the keyfile
        """

        private_key = paramiko.RSAKey.from_private_key_file(private_keyfile)
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        while True:
            try:
                self.ssh_client.connect(hostname=hostname, username=usrname, pkey=private_key)
            except paramiko.ssh_exception.NoValidConnectionsError as e:
                time.sleep(5)
            else:
                break

        # Open SFTP 
        self.ftp_client=self.ssh_client.open_sftp()

    def exec(self, command):
        """ Application of the exec_command method
            Parameter
            ---------
            command: string
                the command to execute
        """
        stdin,stdout,stderr = self.ssh_client.exec_command(command)
    #     exit_status = stdout.channel.recv_exit_status()
        
        
    def close_connection(self):
        """Close the established connection"""
        self.ssh_client.close()

    def get_file(self,remote_path, local_path):
        """Get a file from an instance"""
        self.ftp_client.get(remotepath=remote_path, localpath=local_path)

    def upload_file(self,remote_path, local_path):
        """upload a file on an instance"""
        self.ftp_client.put(remotepath=remote_path,localpath=local_path)
    
