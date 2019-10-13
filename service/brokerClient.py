import time
import Pyro4
import shortuuid


def connect_to_heartbeat_broker():
    uri = "PYRONAME:heartbeatBroker@localhost:1337"
    return Pyro4.Proxy(uri)


@Pyro4.expose
class AllToAllHeartbeat:
    def __init__(self):
        self.server_status = 0
        self.client_id = shortuuid.uuid()
        self.heartbeat_broker = connect_to_heartbeat_broker()
        self.ping_heartbeat_broker()

    def acknowledge(self):
        return "client " + self.client_id + " is healthy"

    def ping_heartbeat_broker(self):
        print 'pinging heartbeat broker'
        print self.heartbeat_broker.ack(self.client_id)

    def all_to_all_heartbeat_ping(self):
        while True:
            if self.server_status:
                print 'trying to ping broker'
                print self.heartbeat_broker.broadcast()
                time.sleep(3)
