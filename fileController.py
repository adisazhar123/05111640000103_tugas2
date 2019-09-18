import os

class FileController(object):
    def __init__(self):
        pass

    def incoming_requests(self, type, name=None, body=None):
        if type == 'CREATE_FILE':
            return self.create_file(name, body)

    def create_file(self, name, body):
        path = "storage/" + name
        fout = open(path, "wb+")
        fout.write(body)
        fout.close()
        return "ok. file created"

    def test(self, body):
        return "request body is : " + body

if __name__ == '__main__':
    fc = FileController()
    print(fc.test(''))
    print(fc.create_file('',''))