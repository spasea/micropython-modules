import urequests
import machine
import uasyncio
import utime
import uos
import random

from .logger import write


class Task:
    def __init__(self, method="", name="", time_start=0, time_end=0, time_diff=0, payload=None, _id=0):
        if payload is None:
            payload = {}

        if _id == 0:
            _id = utime.time() + random.randint(0, 2000)

        self.method = method
        self.name = name
        self.time_start = time_start
        self.time_end = time_end
        self.time_diff = time_diff
        self.payload = payload
        self.id = _id

    def is_repeatable(self):
        return self.time_start < self.time_end or self.time_end == 0

    def storage_data(self):
        key = '/'.join(
            [self.name, self.method, str(self.time_start), str(self.time_end), str(self.time_diff), str(self.id)])

        return [key, self.payload]

    def from_storage(self, key, payload):
        [name, method, time_start, time_end, time_diff, _id] = key.split('/')

        self.name = name
        self.method = method
        self.time_start = int(time_start)
        self.time_end = int(time_end)
        self.time_diff = int(time_diff)
        self.id = int(_id)
        self.payload = payload

        return self


class Tasks:
    def __init__(self, on_ready, sync_time=False):
        if sync_time:
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
        filters = {}

        def get_handler():
            satisfied_tasks = {}

            for key in self.time_object:
                task = Task().from_storage(key, self.time_object[key])

                is_satisfied = True

                for idx in filters:
                    filter = filters[idx]

                    is_satisfied = is_satisfied and filter(task)

                if not is_satisfied:
                    continue

                satisfied_tasks[key] = self.time_object[key]

            return satisfied_tasks

        methods = {
            'get': get_handler
        }

        def add_filter(handler):
            key = uos.urandom(10)
            filters[key] = handler

        def add_method(method):
            if method:
                add_filter(lambda task: method == task.method)

            return methods

        methods['add_method'] = add_method

        def add_name(name):
            if name:
                add_filter(lambda task: name == task.name)

            return methods

        methods['add_name'] = add_name

        def add_from_time_start(time_start):
            if time_start:
                add_filter(lambda task: time_start < task.time_start)

            return methods

        methods['add_from_time_start'] = add_from_time_start

        def add_to_time_start(time_start):
            if time_start:
                add_filter(lambda task: time_start >= task.time_start)

            return methods

        methods['add_to_time_start'] = add_to_time_start

        def add_from_time_end(time_end):
            if time_end:
                add_filter(lambda task: time_end < task.time_end)

            return methods

        methods['add_from_time_end'] = add_from_time_end

        def add_to_time_end(time_end):
            if time_end:
                add_filter(lambda task: time_end >= task.time_end)

            return methods

        methods['add_to_time_end'] = add_to_time_end

        def add_from_time_diff(time_diff):
            if time_diff:
                add_filter(lambda task: time_diff < task.time_diff)

            return methods

        methods['add_from_time_diff'] = add_from_time_diff

        def add_to_time_diff(time_diff):
            if time_diff:
                add_filter(lambda task: time_diff >= task.time_diff)

            return methods

        methods['add_to_time_diff'] = add_to_time_diff

        def add_ids(ids):
            if len(ids):
                add_filter(lambda task: str(task.id) in ids)

            return methods

        methods['add_ids'] = add_ids

        return methods

    def add_task(self, method, name, time_start, time_end, time_diff, payload, _id=0):
        task = Task(method, name, time_start, time_end, time_diff, payload, _id)
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

                if can_repeat_task:
                    self.add_task(task.method, task.name, current_time + task.time_diff, task.time_end, task.time_diff,
                                  task.payload, task.id)

                handler_name = '/'.join([task.name, task.method])
                if handler_name in self.methods_object:
                    try:
                        await self.methods_object[handler_name](task.payload)
                    except Exception as e:
                        print('tasks main loop: ' + str(e) + '\n' + handler_name + ': ' + str(task.payload))
                        write('tasks main loop: ' + str(e) + '\n' + handler_name + ': ' + str(task.payload))
                        print('----\n')
