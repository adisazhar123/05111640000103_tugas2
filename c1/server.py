from c1.fileserver import  *
import Pyro4
import sys

# namainstance = sys.argv[1] or "fileserver"
namainstance = "fileserver"

def start_without_ns():
    daemon = Pyro4.Daemon()
    x_FileServer = Pyro4.expose(FileServer)
    uri = daemon.register(x_FileServer)
    print("my URI : ", uri)
    daemon.requestLoop()


def start_with_ns():
    #name server harus di start dulu dengan  pyro4-ns -n localhost -p 7777
    #gunakan URI untuk referensi name server yang akan digunakan
    #untuk mengetahui instance apa saja yang aktif gunakan pyro4-nsc -n localhost -p 7777 list

    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 7777)
    x_FileServer = Pyro4.expose(FileServer)
    uri_fileserver = daemon.register(x_FileServer)
    ns.register("{}" . format(namainstance), uri_fileserver)
    #untuk instance yang berbeda, namailah fileserver dengan angka
    ns.register("fileserver2", uri_fileserver)
    ns.register("fileserver3", uri_fileserver)
    daemon.requestLoop()


if __name__ == '__main__':
    start_with_ns()
