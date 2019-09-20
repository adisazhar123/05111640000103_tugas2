import os


class FileController(object):
    def __init__(self):
        self.current_working_path = os.getcwd() + "/serverStorage"

    def create_file(self, name, body):
        # return 'in here'
        path = self.current_working_path + "/" + name
        # return path
        f = open(path, 'wb+')
        f.write(body)
        f.close()
        return "ok. file created"

    def list_files(self):
        return os.listdir(self.current_working_path)

    def change_dir(self, path):
        wanted_path = self.current_working_path + '/' + path
        if not os.path.exists(wanted_path):
            return 'Path not found'
        os.chdir(wanted_path)
        self.current_working_path = os.getcwd()
        return 'Moved path succesfully. Now in path ' + self.current_working_path

    def delete_file(self, name):
        to_be_deleted_path = self.current_working_path + '/' + name
        if not os.path.isfile(to_be_deleted_path):
            return 'File not found'
        os.remove(to_be_deleted_path)
        return 'File has been deleted'

    def test(self, body):
        return "request body is : " + body

    def read_file(self, name):
        path = self.current_working_path + '/' + name
        if not os.path.isfile(path):
            return "File not found"
        f = open(path, 'rb')
        binary_file = f.read()
        f.close()
        return binary_file


if __name__ == '__main__':
    fc = FileController()
