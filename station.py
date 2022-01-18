import sys

import network
import utime

from .lamp import Lamp
from .logger import writer
from .tasks import tasks_instance

station_writer = writer('Station')
lamp_writer = writer('Lamp')


class Station:
    def __init__(self, ssid='', password='', single_string='', lamp: Lamp or None = None):
        self.station = ''
        self.lamp = lamp
        self.is_lamp_blinking = False

        if single_string != '':
            self.single_string = single_string
            self.add_tasks()
            try:
                self.find()
            except Exception as e:
                station_writer(e)

            return

        self.password = password
        self.ssid = ssid

        self.add_tasks()
        try:
            self.connect()
        except Exception as e:
            station_writer(e)

    def add_tasks(self):
        now_time = utime.time()

        tasks_instance.add_method('station:check-connection', 'non-savable', self.check_connection)
        # year in seconds
        tasks_instance.add_task('station:check-connection', 'non-savable', now_time, now_time + 86400*365, 15, {})

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

            self.lamp.blink(2)

    async def check_connection(self, task):
        def turn_off_lamp():
            for key in tasks_instance.get_tasks()['add_method']('lamp-indicator')['add_module']('station')['get']():
                tasks_instance.delete_task(key)

            self.is_lamp_blinking = False

        if self.station and self.station.isconnected():
            turn_off_lamp()

            return

        if self.lamp and not self.is_lamp_blinking:
            now_time = utime.time()
            lamp_inst = self.lamp

            async def handler(task):
                lamp_writer('Lamp blinking')
                lamp_inst.blink(3)

            tasks_instance.add_method('lamp-indicator', 'station', handler)
            # year in seconds
            tasks_instance.add_task('lamp-indicator', 'station', now_time, now_time + 86400*365, 15, {})
            self.is_lamp_blinking = True

        try:
            self.find()
            turn_off_lamp()
        except Exception as e:
            sys.print_exception(e)
            station_writer(e)
