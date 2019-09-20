import Pyro4
import os
import tempfile
import subprocess

def connect_server():
    uri = "PYRONAME:fileControllerServer@localhost:1337"
    return Pyro4.Proxy(uri)


class Client:
    def __init__(self):
        self.fc_server = connect_server()
        self.current_working_path = os.getcwd() + '/' + 'clientStorage'
        print 'Connected to remote server!'
        self.show_help_server()

    def show_help_server(self):
        print "[COMMANDS]\n1. list files - lsserver\n2. upload file - upload [filename]\n3. change directory - cdserver [path]\n4. delete file - rm [filename]\n5. update file (text) - update [filename].\n6. download file - read [filename]\n7. change client directory - cdclient [path]\n8. list client files - lsclient"

    def upload_file(self, name):
        full_path = self.current_working_path + '/' + name
        if not os.path.isfile(full_path):
            return 'File not found. full path is', full_path
        with open(full_path, 'rb') as f:
            file_binary = f.read()
        return self.fc_server.create_file(name, file_binary)

    def update_file(self, path, original_file_name):
        if not os.path.isfile(path):
            return 'File not found'
        with open(path, 'rb') as f:
            file_binary = f.read()
        print 'original file name', original_file_name
        return self.fc_server.create_file(original_file_name, file_binary)

    def change_dir_client(self, path):
        wanted_path = self.current_working_path + '/' + path
        if not os.path.exists(wanted_path):
            return 'Path not found'
        os.chdir(wanted_path)
        self.current_working_path = os.getcwd()
        return 'Moved path succesfully. Now in path ' + self.current_working_path

    def list_files_client(self):
        return os.listdir(self.current_working_path)

    def delete_file(self, file_name):
        return self.fc_server.delete_file(file_name)

    def listen_command(self):
        while True:
            command = raw_input()
            split_command = command.split(' ')
            if split_command[0] == 'lsserver':
                for f in self.fc_server.list_files():
                    print f
            elif split_command[0] == 'lsclient':
                for f in self.list_files_client():
                    print f
            elif split_command[0] == 'cdserver':
                dir_name = split_command[1]
                print self.fc_server.change_dir(dir_name)
            elif split_command[0] =='cdclient':
                dir_name = split_command[1]
                print self.change_dir_client(dir_name)
            elif split_command[0] == 'upload':
                file_name = split_command[1]
                print self.upload_file(file_name)
            elif split_command[0] == 'rm':
                file_name = split_command[1]
                print self.delete_file(file_name)
            elif split_command[0] == 'read':
                file_name = split_command[1]
                server_response = self.fc_server.read_file(file_name)

                f = open(self.current_working_path + '/' + file_name, 'wb+')
                f.write(server_response)
                f.close()
            elif split_command[0] == 'update':
                print 'in update'
                file_name = split_command[1]
                server_response = self.fc_server.read_file(file_name)

                f = tempfile.NamedTemporaryFile(delete=False)
                f.write(server_response)
                f.close()
                path = f.name
                subprocess.call(['nano', path])
                print self.update_file(path, file_name)
            else:
                print 'Command not recognised.'


if __name__ == '__main__':
    client = Client()
    client.listen_command()
