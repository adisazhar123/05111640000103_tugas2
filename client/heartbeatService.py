import time

import Pyro4


class Singleton(object):
  _instances = {}
  def __new__(class_, *args, **kwargs):
    if class_ not in class_._instances:
        class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)
    return class_._instances[class_]


@Pyro4.expose
class HeartBeatService(Singleton):
    def __init__(self):
        self.heartbeat_received = 0
        self.heartbeat_received_at = time.time()

    def receive_heartbeat(self):
        self.heartbeat_received = self.heartbeat_received + 1
        self.heartbeat_received_at = time.time()
        return 'heartbeat received yay!'
