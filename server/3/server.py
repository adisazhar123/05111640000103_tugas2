import time
import Pyro4
import threading
import sys
import os

sys.path.append(os.path.abspath("/home/adisazhar/projects/python/05111640000103_tugas2"))

from Pyro4.errors import CommunicationError
from fileController import FileController
from service.brokerClient import AllToAllHeartbeat


def start_server(file_controller_obj):
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 1337)
    uri_file_controller = daemon.register(file_controller_obj)
    print('URI file controller server: ', uri_file_controller)
    ns.register("fileControllerServer_3", uri_file_controller)
    daemon.requestLoop()


def start_all_to_all_heartbeat_server(all_to_all_heartbeat_obj):
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 1337)
    uri_all_to_all_heartbeat = daemon.register(all_to_all_heartbeat_obj)
    print 'URI all to all heart beat server exposed by client: ', uri_all_to_all_heartbeat
    print 'all to all heartbeat server .... client id', all_to_all_heartbeat_obj.client_id
    ns.register("allToAllHeartbeatByClient_" + all_to_all_heartbeat_obj.client_id, uri_all_to_all_heartbeat)
    all_to_all_heartbeat_obj.server_status = 1
    daemon.requestLoop()


def connect_to_heartbeat_service():
    try:
        uri = "PYRONAME:heartbeatServiceServer@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print 'lalala'


def heartbeat():
    print 'connecting to heartbeatServer'
    time.sleep(3)
    heartbeat_server = connect_to_heartbeat_service()
    heartbeat_count = 0
    while True:
        try:
            print heartbeat_server.receive_heartbeat(heartbeat_count)
            heartbeat_count = heartbeat_count + 1
            time.sleep(3)
        except CommunicationError as e:
            print 'Failure detected. Client suspected of disconnecting.', e.message


if __name__ == "__main__":
    # Uncomment for heartbeat
    # heartbeatThread = threading.Thread(target=heartbeat)
    # heartbeatThread.daemon = True
    # heartbeatThread.start()

    # Uncomment for all to all heartbeat
    # all_to_all_heartbeat_server_obj = AllToAllHeartbeat()
    # all_to_all_heartbeat_server = threading.Thread(target=start_all_to_all_heartbeat_server,
    #                                                args=(all_to_all_heartbeat_server_obj,))
    # all_to_all_heartbeat_server.daemon = True
    # all_to_all_heartbeat_server.start()
    #
    # all_to_all_heartbeat_ping_thread = threading.Thread(
    #     target=all_to_all_heartbeat_server_obj.all_to_all_heartbeat_ping)
    # all_to_all_heartbeat_ping_thread.daemon = True
    # all_to_all_heartbeat_ping_thread.start()

    file_controller_obj = FileController()
    start_server(file_controller_obj)
