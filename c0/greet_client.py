import Pyro4

def test_no_ns():
    uri = "PYRO:obj_27d7c59497c44c688319f7d8a4a95935@localhost:40549"
    gserver = Pyro4.Proxy(uri)
    print(gserver.get_greet('ronaldo'))

def test_with_ns():
    uri = "PYRONAME:greetserver@localhost:7777"
    gserver = Pyro4.Proxy(uri)
    print(gserver.get_greet('ronaldo'))

if __name__=='__main__':
    test_with_ns()
