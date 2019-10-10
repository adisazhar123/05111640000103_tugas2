import time

import Pyro4
import os
import tempfile
import subprocess
import threading

from Pyro4.errors import ConnectionClosedError, CommunicationError

from heartbeatService import HeartBeatService


def connect_server():
    try:
        uri = "PYRONAME:fileControllerServer@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print 'lalala'


def start_heartbeat_service(hb_service):
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 1337)
    # x_heartbeat_service = Pyro4.expose(hb_service)
    # uri_heartbeat_service = daemon.register(x_heartbeat_service)
    uri_heartbeat_service = daemon.register(hb_service)
    print('URI heartbeat service server: ', uri_heartbeat_service)
    ns.register("heartbeatServiceServer", uri_heartbeat_service)
    daemon.requestLoop()


def detect_heatbeat_failure(hb_service):
    while True:
        if time.time() - hb_service.heartbeat_received_at > 3:
            print 'heartbeat failure detected'
            break
    return


class Client:
    def __init__(self):
        self.fc_server = connect_server()
        self.current_working_path = os.getcwd() + '/' + 'clientStorage'
        print 'Connected to remote server!'
        self.show_help_server()

    def show_help_server(self):
        print "[COMMANDS]\n1. list files - lsserver\n2. upload file - upload [filename]\n3. change directory - cdserver [path]\n4. delete file - rm [filename]\n5. update file (text) - update [filename].\n6. download file - read [filename]\n7. change client directory - cdclient [path]\n8. list client files - lsclient"

    def upload_file(self, name):
        try:
            full_path = self.current_working_path + '/' + name
            if not os.path.isfile(full_path):
                return 'File not found. full path is', full_path
            with open(full_path, 'rb') as f:
                file_binary = f.read()
            return self.fc_server.create_file(name, file_binary)
        except CommunicationError as e:
            print 'failure detected', e.message

    def update_file(self, path, original_file_name):
        try:
            if not os.path.isfile(path):
                return 'File not found'
            with open(path, 'rb') as f:
                file_binary = f.read()
            print 'original file name', original_file_name
            return self.fc_server.create_file(original_file_name, file_binary)
        except CommunicationError as e:
            print 'failure detected', e.message

    def change_dir_client(self, path):
        try:
            wanted_path = self.current_working_path + '/' + path
            if not os.path.exists(wanted_path):
                return 'Path not found'
            os.chdir(wanted_path)
            self.current_working_path = os.getcwd()
            return 'Moved path succesfully. Now in path ' + self.current_working_path
        except CommunicationError as e:
            print 'failure detected', e.message

    def list_files_client(self):
        try:
            return os.listdir(self.current_working_path)
        except CommunicationError as e:
            print 'failure detected', e.message

    def delete_file(self, file_name):
        try:
            return self.fc_server.delete_file(file_name)
        except CommunicationError as e:
            print 'failure detected', e.message

    def ping(self):
        while True:
            try:
                start = time.time()
                ack = self.fc_server.ping()
                end = time.time()
                # print 'took ', end-start, ' seconds'
                if end-start > 3:
                    break
                time.sleep(3)
            except ConnectionClosedError as e:
                break
            except CommunicationError as e:
                break
        print 'Server is not responding. Failure detected!'
        return

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
                file_name = " ".join(split_command[1:])
                print self.upload_file(file_name)
            elif split_command[0] == 'rm':
                file_name = " ".join(split_command[1:])
                print self.delete_file(file_name)
            elif split_command[0] == 'read':
                file_name = " ".join(split_command[1:])
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
    pingThread = threading.Thread(target=client.ping)
    pingThread.daemon = True
    pingThread.start()

    hbService = HeartBeatService()
    heartbeatServer = threading.Thread(target=start_heartbeat_service, args=(hbService,))
    heartbeatServer.daemon = True
    heartbeatServer.start()

    hbFailureDetection = threading.Thread(target=detect_heatbeat_failure, args=(hbService,))
    hbFailureDetection.daemon = True
    hbFailureDetection.start()

    client.listen_command()
