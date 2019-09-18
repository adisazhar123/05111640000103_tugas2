import Pyro4


def connect_server():
    uri = "PYRONAME:fileControllerServer@localhost:1337"
    fcServer = Pyro4.Proxy(uri)
    print(fcServer.test("lmao my man"))


if __name__ == '__main__':
    connect_server()
