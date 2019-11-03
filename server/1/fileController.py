import os

import Pyro4


def connect_to_replication_server():
    uri = "PYRONAME:replicationController@localhost:1337"
    return Pyro4.Proxy(uri)


@Pyro4.expose
class FileController(object):
    def __init__(self):
        self.instance_name = "fileControllerServer_1"
        self.current_working_path = os.getcwd() + "/serverStorage"
        self.replication_server = connect_to_replication_server()
        self.replication_server.file_servers_on_connect(self.instance_name)

    def create_file(self, name, body):
        # return 'in here'
        path = self.current_working_path + "/" + name
        # return path
        f = open(path, 'wb+')
        f.write(body)
        f.close()
        replication_response = self.replication_server.hello_world(self.instance_name, name, body, 'CREATE')
        print replication_response
        return "ok. file created"

    # START this needs to be copied to each file controllers
    def replicate_file(self, name, body):
        path = self.current_working_path + "/" + name
        f = open(path, 'wb+')
        f.write(body)
        f.close()
        return "ok. file created"

    def delete_file_replication(self, name):
        to_be_deleted_path = self.current_working_path + '/' + name
        if not os.path.isfile(to_be_deleted_path):
            return 'File not found'
        os.remove(to_be_deleted_path)
        return 'File has been deleted'

    # END ====================

    def list_files(self):
        return os.listdir(self.current_working_path)

    def change_dir(self, path):
        wanted_path = self.current_working_path + '/' + path
        if not os.path.exists(wanted_path):
            return 'Path not found'
        os.chdir(wanted_path)
        self.current_working_path = os.getcwd()
        return 'Moved path succesfully. Now in path ' + self.current_working_path

    def delete_file(self, name):
        to_be_deleted_path = self.current_working_path + '/' + name
        if not os.path.isfile(to_be_deleted_path):
            return 'File not found'
        os.remove(to_be_deleted_path)
        replication_response = self.replication_server.hello_world(self.instance_name, name, '', 'DELETE')
        print replication_response
        return 'File has been deleted'

    def test(self, body):
        return "request body is : " + body

    def read_file(self, name):
        path = self.current_working_path + '/' + name
        if not os.path.isfile(path):
            return "File not found"
        f = open(path, 'rb')
        binary_file = f.read()
        f.close()
        return binary_file

    def ping(self):
        return "ok from server"


if __name__ == '__main__':
    fc = FileController()
