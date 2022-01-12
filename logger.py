import utime
import os


def write_to_file(string, file):
    file = open(file, 'a')
    file.write('\n' + string)
    print(string)
    file.close()


def write(string):
    write_to_file(string, './log.txt')


def writer(name, file='./log.txt'):
    time_initialized = utime.time()

    def handler(string):
        next_time = utime.time()
        nonlocal time_initialized
        diff = next_time - time_initialized
        time_initialized = utime.time()
        write_to_file('[' + name + ', ' + str(next_time) + ']: ' + str(string) + '; +' + str(diff), file)

    return handler


def get_logs(file_path):
    try:
        is_file_exists = os.stat(file_path)

        if is_file_exists:
            return file_path

        raise OSError('No such file')
    except OSError:
        file = open(file_path, 'a')
        file.write('')
        file.close()
        return file_path


def read_logs(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except OSError:
        file = open(file_path, 'a')
        file.write('')
        file.close()
        return ''
