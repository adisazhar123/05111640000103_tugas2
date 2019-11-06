from c0.greet import  *
import Pyro4


def start_without_ns():
    daemon = Pyro4.Daemon()
    x_GreetServer = Pyro4.expose(GreetServer)
    uri = daemon.register(x_GreetServer)
    print("my URI : ", uri)
    daemon.requestLoop()


def start_with_ns():
    #name server harus di start dulu dengan  pyro4-ns -n localhost -p 7777
    #gunakan URI untuk referensi name server yang akan digunakan
    #untuk mengecek service apa yang ada di ns, gunakan pyro4-nsc -n localhost -p 7777 list
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost",7777)
    x_GreetServer = Pyro4.expose(GreetServer)
    uri_greetserver = daemon.register(x_GreetServer)
    print("URI greet server : ", uri_greetserver)
    ns.register("greetserver", uri_greetserver)
    daemon.requestLoop()


if __name__ == '__main__':
    start_with_ns()
