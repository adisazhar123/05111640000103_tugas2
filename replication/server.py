import os
import sys

import Pyro4
import threading
sys.path.append(os.path.abspath("/home/adisazhar/projects/python/05111640000103_tugas2"))

from replication.controller import ReplicationController


def start_server(replication_controller_obj):
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 1337)
    uri_replication_controller = daemon.register(replication_controller_obj)
    print('URI replication_controller server: ', uri_replication_controller)
    ns.register("replicationController", uri_replication_controller)
    daemon.requestLoop()


if __name__ == '__main__':
    replication_controller = ReplicationController()
    replication_controller_thread = threading.Thread(target=replication_controller.listen_to_files_to_replicate)
    replication_controller_thread.daemon = True
    replication_controller_thread.start()

    start_server(replication_controller)
