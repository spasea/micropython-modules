import utime


def write(string):
    file = open('./log.txt', 'a')
    file.write('\n' + string)
    file.write('\n' + '----' + str(utime.time()) + '----')
    file.close()
