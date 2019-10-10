import time

import Pyro4
import threading

from Pyro4.errors import CommunicationError

from fileController import FileController


def start_server():
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 1337)
    x_file_controller = Pyro4.expose(FileController)
    uri_file_controller = daemon.register(x_file_controller)
    print('URI file controller server: ', uri_file_controller)
    ns.register("fileControllerServer", uri_file_controller)
    daemon.requestLoop()


def connect_to_heartbeat_service():
    try:
        uri = "PYRONAME:heartbeatServiceServer@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print 'lalala'


def heartbeat():
    heartbeatServer = connect_to_heartbeat_service()
    print 'connect to heartbeatServer'
    time.sleep(3)
    while True:
        try:
            print heartbeatServer.receive_heartbeat()
            time.sleep(2)
        except CommunicationError as e:
            print 'lalala', e.message

if __name__ == "__main__":
    heartbeatThread = threading.Thread(target=heartbeat)
    heartbeatThread.daemon = True
    heartbeatThread.start()
    start_server()
