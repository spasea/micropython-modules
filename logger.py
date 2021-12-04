import utime


def write_error(string, file):
    file = open(file, 'a')
    file.write('\n' + string)
    file.write('\n' + '----' + str(utime.time()) + '----')
    file.close()


def write(string):
    write_error('./log.txt', string)
