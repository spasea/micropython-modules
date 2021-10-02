import uasyncio


class Timed:
    def __init__(self, on_handler, off_handler):
        self.off_handler = off_handler
        self.on_handler = on_handler
        self.current_task = ''

    async def task(self, time_base, on_percent):
        print('before on message')
        await uasyncio.sleep(6)
        print('on message')
        await uasyncio.sleep(4)
        print('off message')

    def start(self, path):
        time_base = ''
        on_percent = ''

        print('----------start----------')

        # if self.current_task != '':
        #     try:
        #         self.current_task.cancel()
        #     except Exception as e:
        #         print(e)
        #
        #     self.current_task = ''

        # uasyncio.new_event_loop()
        self.current_task = uasyncio.create_task(self.task(time_base, on_percent))

        return {'time': time_base, 'on_percent': on_percent}

    def break_task(self, path):
        try:
            self.current_task.cancel()
        except Exception as e:
            print(e)

        print('stop task')

        return {'state': 'stopped'}
