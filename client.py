import Pyro4
from Pyro4.util import SerializerBase
import os


def connect_server():
    uri = "PYRONAME:fileControllerServer@localhost:1337"
    return Pyro4.Proxy(uri)


class Client:
    def __init__(self):
        self.fc_server = connect_server()
        self.current_working_path = os.getcwd() + '/' + 'clientStorage'
        print 'Connected to remote server!'
        self.show_help()

    def show_help(self):
        print "1. list files - ls\n2. upload file - upload [filename]\n"

    def upload_file(self, name):
        full_path = self.current_working_path + '/' + name
        if not os.path.isfile(full_path):
            return 'File not found'
        with open(full_path, 'rb') as f:
            file_binary = f.read()
        return self.fc_server.create_file(name, file_binary)

    def listen_command(self):
        while True:
            command = raw_input()
            print 'command is ' + command
            split_command = command.split(' ')
            if split_command[0] == 'ls':
                for f in self.fc_server.list_files():
                    print f
            elif split_command[0] == 'cd':
                dir_name = split_command[1]
                print self.fc_server.change_dir(dir_name)
            elif split_command[0] == 'upload':
                file_name = split_command[1]
                print self.upload_file(file_name)
            elif split_command[0] == 'rm':
                file_name = split_command[1]
                print self.delete_file(file_name)
            elif split_command[0] == 'read':
                print 'in read'
                file_name = split_command[1]
                server_response = self.fc_server.read_file(file_name)

                f = open(self.current_working_path + '/' + file_name, 'wb+')
                f.write(server_response)
                f.close()

    def delete_file(self, file_name):
        return self.fc_server.delete_file(file_name)


if __name__ == '__main__':
    client = Client()
    client.listen_command()
