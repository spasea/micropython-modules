import network


class Station:
    def __init__(self, ssid, password):
        self.password = password
        self.ssid = ssid
        self.station = ''

        self.connect()

    def connect(self):
        station = network.WLAN(network.STA_IF)
        station.active(True)

        station.disconnect()

        self.station = station

        if not station.isconnected():
            station.connect(self.ssid, self.password)

            while not station.isconnected():
                pass
