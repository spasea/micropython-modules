from machine import Pin
import time


class Lamp:
    def __init__(self, id=2):
        self.led = Pin(id, Pin.OUT)

    def toggle(self):
        value = self.led.value()
        self.led.value(0 if value == 1 else 1)

    def blink(self, times):
        prev_value = self.led.value()
        self.led.value(0)

        if prev_value == 1:
            time.sleep(1)

        for x in range(0, times * 2):
            sleep_time = 0 if x % 2 else 1
            time.sleep((sleep_time + 0.5) * 0.25)

            self.toggle()
