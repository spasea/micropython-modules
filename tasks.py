import urequests
import machine
import uasyncio
import utime


class Task:
    def __init__(self, method="", name="", time_start=0, time_end=0, time_diff=0, payload={}):
        self.method = method
        self.name = name
        self.time_start = time_start
        self.time_end = time_end
        self.time_diff = time_diff
        self.payload = payload

    def is_repeatable(self):
        return self.time_start < self.time_end or self.time_end == 0

    def storage_data(self):
        key = '/'.join([self.name, self.method, str(self.time_start), str(self.time_end), str(self.time_diff)])

        return [key, self.payload]

    def from_storage(self, key, payload):
        [name, method, time_start, time_end, time_diff] = key.split('/')

        self.name = name
        self.method = method
        self.time_start = int(time_start)
        self.time_end = int(time_end)
        self.time_diff = int(time_diff)
        self.payload = payload

        return self


class Tasks:
    def __init__(self, on_ready):
        response = urequests.get('http://worldtimeapi.org/api/timezone/Europe/Kiev')
        object = response.json()
        [date, time] = object['datetime'].split('T')
        [year, month, day] = date.split('-')
        [hours, minutes, seconds] = time[0:8].split(':')
        rtc = machine.RTC()
        rtc.init((int(year), int(month), int(day), int(hours), int(minutes), int(seconds), 0, 0))

        on_ready()

        self.time_object = {}
        self.methods_object = {}

    def add_method(self, module, method, callback):
        self.methods_object['/'.join([module, method])] = callback

        return self.methods_object

    def get_tasks(self):
        return self.time_object

    def add_task(self, method, name, time_start, time_end, time_diff, payload):
        task = Task(method, name, time_start, time_end, time_diff, payload)
        [key, _payload] = task.storage_data()

        self.time_object[key] = _payload

        return {'key': key, 'payload': payload}

    def delete_task(self, key):
        if not key in self.time_object:
            return self.time_object

        del self.time_object[key]

        return self.time_object

    def check_task_validity(self, key, payload):
        current_time = utime.time()

        task = Task().from_storage(key, payload)

        is_task_valid = task.time_end >= current_time
        can_execute_task = is_task_valid and task.time_start < current_time
        can_repeat_task = can_execute_task and current_time + task.time_diff <= task.time_end

        if not is_task_valid:
            self.delete_task(task.storage_data()[0])

        return [is_task_valid, can_execute_task, can_repeat_task]

    async def main(self):
        while True:
            await uasyncio.sleep(5)

            current_time = utime.time()

            for key in self.time_object:
                payload = self.time_object[key]

                [is_task_valid, can_execute_task, can_repeat_task] = self.check_task_validity(key, payload)

                if not is_task_valid or not can_execute_task:
                    continue

                self.delete_task(key)

                task = Task().from_storage(key, payload)

                handler_name = '/'.join([task.name, task.method])
                if handler_name in self.methods_object:
                    await self.methods_object[handler_name](task.payload)

                if not can_repeat_task:
                    continue

                self.add_task(task.method, task.name, current_time + task.time_diff, task.time_end, task.time_diff, task.payload)
