import random


class GreetServer(object):
    def __init__(self):
        pass

    def get_greet(self, name='NoName'):
        lucky_number = random.randint(1, 100000)
        return "Hello {}, this is your lucky number {}".format(name, lucky_number)


if __name__ == '__main__':
    k = GreetServer()
    print(k.get_greet('royyana'))
