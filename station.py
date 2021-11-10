import network


class Station:
    def __init__(self, ssid, password):
        self.password = password
        self.ssid = ssid
        self.station = ''

        self.connect()

    def connect(self):
        station = network.WLAN(network.STA_IF)

        self.station = station

        if not station.isconnected():
            station.active(True)
            station.connect(self.ssid, self.password)

            while not station.isconnected():
                pass
