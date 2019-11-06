import time
import Pyro4
import tempfile
import subprocess
import threading
import sys
import os

sys.path.append(os.path.abspath("/home/adisazhar/projects/python/05111640000103_tugas2"))

from Pyro4.errors import ConnectionClosedError, CommunicationError
from heartbeatService import HeartBeatService
from service.brokerClient import AllToAllHeartbeat


# class ReplicationClient:
#     def __init__(self):
#         pass
#
#     def


# def start_exposing_replication():


def connect_server(file_server_instance_name):
    try:
        uri = "PYRONAME:" + file_server_instance_name + "@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print 'lalala'


def start_heartbeat_service(hb_service):
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 1337)
    uri_heartbeat_service = daemon.register(hb_service)
    print('URI heartbeat service server: ', uri_heartbeat_service)
    ns.register("heartbeatServiceServer", uri_heartbeat_service)
    daemon.requestLoop()


def detect_heatbeat_failure(hb_service, client):
    time_unit = 3
    try:
        while True:
            how_long_it_took = time.time() - hb_service.heartbeat_received_at
            if how_long_it_took > time_unit:
                print '[HEARTBEAT] failure detected', how_long_it_took
                break
        client.failure_detected = 1
        time.sleep((hb_service.heartbeat_received + 1) * time_unit)
    except Exception as e:
        print e.message
        exit()
    return

def start_all_to_all_heartbeat_server_by_client(all_to_all_heartbeat_obj):
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 1337)
    uri_all_to_all_heartbeat = daemon.register(all_to_all_heartbeat_obj)
    print 'URI all to all heart beat server exposed by client: ', uri_all_to_all_heartbeat
    print 'all to all heartbeat server .... client id', all_to_all_heartbeat_obj.client_id
    ns.register("allToAllHeartbeatByClient_" + all_to_all_heartbeat_obj.client_id, uri_all_to_all_heartbeat)
    all_to_all_heartbeat_obj.server_status = 1
    daemon.requestLoop()


class Client:
    def __init__(self):
        self.failure_detected = 0
        self.file_server_instance_name = 'fileControllerServer_2'
        self.fc_server = connect_server(self.file_server_instance_name)
        self.current_working_path = os.getcwd() + '/' + 'clientStorage'
        print 'Connected to remote server!'
        self.show_help_server()

    def show_help_server(self):
        print "[COMMANDS]\n1. list files - lsserver\n2. upload file - upload [filename]\n3. change directory - cdserver [path]\n4. delete file - rm [filename]\n5. update file (text) - update [filename].\n6. download file - read [filename]\n7. change client directory - cdclient [path]\n8. list client files - lsclient"

    def change_file_server(self):
        names = ["fileControllerServer_1", "fileControllerServer_2", "fileControllerServer_3"]
        print "changing file server"
        for (idx, name) in enumerate(names):
            try:
                self.fc_server = connect_server(name)
                self.fc_server.test("ping")
                self.file_server_instance_name = name
            except CommunicationError as e:
                if idx == 2:
                    print "All servers not available"
                    return
                continue
            except Exception as e:
                if idx == 2:
                    print "All servers not available"
                    return
                continue
        print "file server changed"

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
            self.change_file_server()

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
            self.change_file_server()

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
        try:
            return self.fc_server.delete_file(file_name)
        except CommunicationError as e:
            print 'failure detected', e.message
            self.change_file_server()

    def ping(self):
        time_unit = 3
        while True:
            try:
                start = time.time()
                self.fc_server.ping()
                end = time.time()
                # print 'took ', end-start, ' seconds'
                if end - start > time_unit:
                    break
                time.sleep(time_unit)
            except ConnectionClosedError as e:
                break
            except CommunicationError as e:
                break
        try:
            time.sleep(time_unit)
            self.fc_server.ping()
        except ConnectionClosedError as e:
            time.sleep(time_unit)
        except CommunicationError as e:
            time.sleep(time_unit)
        self.failure_detected = 1
        print '[PING ACK] File controller Server is not responding. Failure detected!'
        return

    def change_dir_server(self, dir_name):
        try:
            return self.fc_server.change_dir(dir_name)
        except CommunicationError as e:
            print 'failure detected', e.message
            self.change_file_server()

    def read_file(self, file_name):
        try:
            server_response = self.fc_server.read_file(file_name)

            f = open(self.current_working_path + '/' + file_name, 'wb+')
            f.write(server_response)
            f.close()
        except CommunicationError as e:
            self.change_file_server()
            return 'failure detected', e.message

    def update_file_server(self, file_name):
        try:
            server_response = self.fc_server.read_file(file_name)

            f = tempfile.NamedTemporaryFile(delete=False)
            f.write(server_response)
            f.close()
            path = f.name
            subprocess.call(['nano', path])
            return self.update_file(path, file_name)
        except CommunicationError as e:
            self.change_file_server()
            return 'failure detected', e.message

    def list_server(self):
        try:
            for f in self.fc_server.list_files():
                print f
        except CommunicationError as e:
            self.change_file_server()
            return 'failure detected', e.message

    def listen_command(self):
        try:
            while True:
                command = raw_input()
                split_command = command.split(' ')
                if self.failure_detected:
                    print 'Failure detected. Exiting...'
                    return

                if split_command[0] == 'lsserver':
                    print self.list_server()
                elif split_command[0] == 'lsclient':
                    for f in self.list_files_client():
                        print f
                elif split_command[0] == 'cdserver':
                    dir_name = split_command[1]
                    self.change_dir_server(dir_name)
                elif split_command[0] == 'cdclient':
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
                    print self.read_file(file_name)
                elif split_command[0] == 'update':
                    file_name = split_command[1]
                    print self.update_file_server(file_name)
                else:
                    print 'Command not recognised.'
        except TypeError:
            exit()


if __name__ == '__main__':

    client = Client()
    client.listen_command()
