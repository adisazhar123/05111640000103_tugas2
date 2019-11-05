import Queue
import threading
from time import sleep

import Pyro4
from Pyro4.errors import CommunicationError


def connect(name):
    try:
        uri = "PYRONAME:" + name + "@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print 'error', e.message


@Pyro4.expose
class ReplicationController:
    def __init__(self):
        self.files_to_replicate = Queue.Queue()
        self.files_to_replicate_errs = Queue.Queue()
        self.file_servers = []

    def file_servers_on_connect(self, name):
        pyro_obj = connect(name)
        self.file_servers.append({'name': name, 'instance': pyro_obj})
        print self.file_servers, 'conected'
        self.start_failed_jobs_thread()
        return "ok"

    def hello_world(self, from_name, file_name, file_content, type):
        try:
            self.put_files_to_queue(from_name, file_name, file_content, type)
        except Exception as e:
            print e
            return e
        return "file put to queue!"

    def put_files_to_queue(self, from_name, file_name, file_content, type):
        document = {'from': from_name, 'file_name': file_name, 'file_content': file_content, 'type': type}
        self.files_to_replicate.put(document)

    def replicate_file(self, file_server, file_server_name, file_name, file_content):
        try:
            file_server.replicate_file(file_name, file_content)
        except Exception as e:
            document = {'failed_instance': file_server, 'file_name': file_name,
                        'file_content': file_content, 'type': 'CREATE', 'exception': e,
                        'failed_instance_name': file_server_name}
            print 'err replicating for file_server', file_server
            self.files_to_replicate_errs.put(document)

    def delete_file(self, file_server, file_server_name, file_name):
        try:
            file_server.delete_file_replication(file_name)
        except Exception as e:
            document = {'failed_instance': file_server, 'file_name': file_name,
                        'type': 'DELETE', 'exception': e, 'failed_instance_name': file_server_name}
            print 'err deleting for file_server', file_server, e.message
            self.files_to_replicate_errs.put(document)

    def listen_to_files_to_replicate(self):
        while True:
            file = self.files_to_replicate.get()
            if file['type'] == 'CREATE' or file['type'] == 'UPDATE':
                for instance in self.file_servers:
                    print 'replicating...'
                    self.replicate_file(instance['instance'], instance['name'], file['file_name'], file['file_content'])
            elif file['type'] == 'DELETE':
                for instance in self.file_servers:
                    print 'deleting...'
                    self.delete_file(instance['instance'], instance['name'], file['file_name'])

    def _process_failed_jobs(self):
        print 'starting failed jobs thread...'
        while not self.files_to_replicate_errs.empty():
            print 'processing failed jobs...'
            file = self.files_to_replicate_errs.get()
            if file['type'] == 'CREATE' or file['type'] == 'UPDATE':
                self.replicate_file(connect(file['failed_instance_name']), file['failed_instance_name'],
                                    file['file_name'], file['file_content'])
            elif file['type'] == 'DELETE':
                self.delete_file(connect(file['failed_instance_name']), file['failed_instance_name'], file['file_name'])
        print 'exiting failed jobs thread...'

    def start_failed_jobs_thread(self):
        failed_jobs_thread = threading.Thread(target=self._process_failed_jobs)
        failed_jobs_thread.daemon = True
        failed_jobs_thread.start()
