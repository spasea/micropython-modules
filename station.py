import network


class Station:
    def __init__(self, ssid='', password='', single_string=''):
        self.station = ''

        if single_string != '':
            self.single_string = single_string
            self.find()

            return

        self.password = password
        self.ssid = ssid

        self.connect()

    def find(self):
        station = network.WLAN(network.STA_IF)
        station.active(True)
        stations = station.scan()
        stations_dict = {}

        for station_item in stations:
            stations_dict[station_item[0].decode()] = ''

        config_stations = self.single_string.split('____')
        station_to_connect = ''

        for config_station in config_stations:
            if station_to_connect != '':
                break

            [ssid, p] = config_station.split('__')

            if ssid not in stations_dict:
                continue

            station_to_connect = config_station

        if station_to_connect == '':
            raise Exception('No available station')

            return

        [ssid, password] = station_to_connect.split('__')

        self.password = password
        self.ssid = ssid

        self.connect()

    def connect(self):
        station = network.WLAN(network.STA_IF)

        self.station = station

        if not station.isconnected():
            station.active(True)
            station.connect(self.ssid, self.password)

            while not station.isconnected():
                pass
