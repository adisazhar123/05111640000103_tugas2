import Pyro4
from fileController import FileController

def start_server():
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 1337)
    x_file_controller = Pyro4.expose(FileController)
    uri_file_controller = daemon.register(x_file_controller)
    print('URI file controller server: ', uri_file_controller)
    ns.register("fileControllerServer", uri_file_controller)
    daemon.requestLoop()


if __name__ == "__main__":
    start_server()
