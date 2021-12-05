import utime


def write_error(string, file):
    file = open(file, 'a')
    file.write('\n' + string)
    file.write('\n' + '----' + str(utime.time()) + '----')
    file.close()


def write(string):
    write_error('./log.txt', string)


def get_logs(file):
    try:
        with open(file, 'r') as file:
            return file.read()
    except OSError:
        file = open(file, 'a')
        file.write('')
        file.close()
        return ''
