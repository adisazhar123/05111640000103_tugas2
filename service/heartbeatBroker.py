import Pyro4
import traceback

from Pyro4.errors import CommunicationError


def start_sever(hb_service):
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 1337)
    # x_heartbeat_service = Pyro4.expose(hb_service)
    # uri_heartbeat_service = daemon.register(x_heartbeat_service)
    uri_heartbeat_service = daemon.register(hb_service)
    print('URI heartbeat broker server: ', uri_heartbeat_service)
    ns.register("heartbeatBroker", uri_heartbeat_service)
    daemon.requestLoop()

def connect(client_id):
    try:
        uri = "PYRONAME:allToAllHeartbeatByClient_" + client_id + "@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print 'lalala'


@Pyro4.expose
class HeartBeatBroker:
    def __init__(self):
        self.connected_clients = []
        self.connected_clients_server = []

    def ack(self, client_id):
        if client_id not in self.connected_clients:
            self.connected_clients.append(client_id)
            uri = "PYRONAME:allToAllHeartbeatByClient_" + client_id + "@localhost:1337"
            pyro_obj = connect(client_id)
            self.connected_clients_server.append(pyro_obj)
        return "[heartbeat broker] your client_id is " + client_id, 'number of connected clients is ' \
               + str(len(self.connected_clients_server))

    def broadcast(self):
        print 'broadcast called'
        client_health = []
        current = None

        try:
            for connected_client in self.connected_clients_server:
                current = connected_client
                res = connected_client.acknowledge()
                client_health.append(res)
        except CommunicationError as e:
            print current
            self.connected_clients_server.remove(current)
            client_health.append("failure detected for" + str(current._pyroUri))
        except Exception as e:
            traceback.print_exc()

        return client_health

hb = HeartBeatBroker()
start_sever(hb)