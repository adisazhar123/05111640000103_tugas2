import Queue
from time import sleep

import Pyro4
from Pyro4.errors import CommunicationError

import random


def connect(name):
    try:
        uri = "PYRONAME:" + name + "@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print 'error', e.message


# def listen_to_files_to_replicate(self):
#     while True:
#         file = self.files_to_replicate.get()
        # for instance in self.file_servers:
        #     if instance['name'] != file['from']:
        #         self.replicate_file(instance['instance'], file['file_name'], file['file_content'])
        # print file


@Pyro4.expose
class ReplicationController:
    def __init__(self):
        self.files_to_replicate = Queue.Queue()
        self.file_servers = []

    def file_servers_on_connect(self, name):
        pyro_obj = connect(name)
        self.file_servers.append({'name': name, 'instance': pyro_obj})
        print self.file_servers, 'conected'

    def hello_world(self, from_name, file_name, file_content):
        try:
            self.put_files_to_queue(from_name, file_name, file_content)
        except Exception as e:
            print e
            return e
        return "file put to queue!"
        # return self.files_to_replicate.put(["wahaha"])

    def put_files_to_queue(self, from_name, file_name, file_content):
        document = {'from': from_name, 'file_name': file_name, 'file_content': file_content}
        self.files_to_replicate.put(document)

    def replicate_file(self, file_server, file_name, file_content):
        file_server.replicate_file(file_name, file_content)

    def listen_to_files_to_replicate(self):
        while True:
            file = self.files_to_replicate.get()
            for instance in self.file_servers:
                if instance['name'] != file['from']:
                    self.replicate_file(instance['instance'], file['file_name'], file['file_content'])
            print file['file_name']