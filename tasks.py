import json

import urequests
import machine
import uasyncio
import utime
import uos
import random

from .logger import writer
from .state_save import StateSaveInterface

tasks_writer = writer('Tasks')


class Task:
    def __init__(self, method="", module="", time_start=0, time_end=0, time_diff=0, payload=None, _id=0,
                 is_last_priority: int = 0):
        if payload is None:
            payload = {}

        if _id == 0:
            _id = utime.time() + random.randint(0, 2000)

        self.method = method
        self.module = module
        self.time_start = time_start
        self.time_end = time_end
        self.time_diff = time_diff
        self.payload = payload
        self.id = _id
        self._async_task = None
        self.is_last_priority = is_last_priority

    def is_repeatable(self):
        return self.time_start < self.time_end or self.time_end == 0

    def storage_data(self):
        key = '/'.join(
            [self.module, self.method, str(self.time_start), str(self.time_end), str(self.time_diff), str(self.id),
             str(self.is_last_priority)])

        return [key, self.payload]

    def from_storage(self, key, payload):
        [module, method, time_start, time_end, time_diff, _id, is_last_priority] = key.split('/')

        self.module = module
        self.method = method
        self.time_start = int(time_start)
        self.time_end = int(time_end)
        self.time_diff = int(time_diff)
        self.id = int(_id)
        self.payload = payload
        self.is_last_priority = int(is_last_priority)

        return self

    def add_async_task(self, async_task):
        self._async_task = async_task

        return self

    def cancel(self):
        if self._async_task is None:
            return self

        self._async_task.cancel()

        return self


class Tasks(StateSaveInterface):
    def __init__(self, on_ready=None, sync_time=False, time_endpoint=None):
        if sync_time:
            _time_endpoint = time_endpoint or 'http://worldtimeapi.org/api/timezone/Europe/Kiev'

            response = urequests.get(_time_endpoint)
            object = response.json()
            [date, time] = object['datetime'].split('T')
            [year, month, day] = date.split('-')
            [hours, minutes, seconds] = time[0:8].split(':')
            rtc = machine.RTC()
            rtc.init((int(year), int(month), int(day), int(hours), int(minutes), int(seconds), 0, 0))

        if on_ready:
            on_ready()

        self.time_object = {}
        self.methods_object = {}

    def to_string(self) -> str:
        tasks_to_delete = self.get_tasks()['add_module']('non-savable')['get']()
        for task_key in tasks_to_delete:
            self.delete_task(task_key)

        return json.dumps(self.time_object)

    def from_string(self, string: str, last_loaded_time: tuple) -> 'Tasks':
        times = json.loads(string)
        self.time_object.update(times)

        return self

    def add_method(self, method, module, callback):
        async def handler(task):
            await callback(task)

        self.methods_object['/'.join([module, method])] = handler

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

                satisfied_tasks[key] = task

            return satisfied_tasks

        methods = {
            'get': get_handler
        }

        def add_filter(handler):
            key = uos.urandom(10)
            filters[key] = handler

        def add_method(method):
            if method:
                add_filter(lambda task: task.method in method.split(','))

            return methods

        methods['add_method'] = add_method

        def add_module(module):
            if module:
                add_filter(lambda task: module == task.module)

            return methods

        methods['add_module'] = add_module

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

    def add_task(self, task: Task):
        [key, _payload] = task.storage_data()

        self.time_object[key] = _payload

        return {'key': key, 'payload': _payload}

    def delete_task(self, key):
        if key not in self.time_object:
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

    async def get_async_tasks(self, async_batch):
        async_list = []

        for handler in async_batch:
            async_list.append(handler())

        await uasyncio.gather(*async_list)

    async def main(self):
        def task_handler(__task, _self):
            _task = Task().from_storage(*json.loads(json.dumps(__task.storage_data())))

            async def handler():
                _task.time_start = utime.time() + _task.time_diff
                _self.add_task(_task)

            return handler

        while True:
            await uasyncio.sleep(random.randint(3, 6))

            tasks_batch = []
            tasks_batch_keys = []
            last_priority_tasks_batch = []
            last_priority_tasks_batch_keys = []
            repeats_batch = []
            repeats_batch_keys = []
            last_index = 0

            for key in self.time_object:
                payload = self.time_object[key]

                [is_task_valid, can_execute_task, can_repeat_task] = self.check_task_validity(key, payload)

                if not is_task_valid or not can_execute_task:
                    continue

                self.delete_task(key)

                task = Task().from_storage(key, payload)

                def append_task(_task: Task, _handler):
                    task_key = _task.storage_data()[0]

                    async def _task_handler():
                        await _handler(_task)

                    if bool(_task.is_last_priority):
                        last_priority_tasks_batch[last_index].append(_task_handler)

                        last_priority_tasks_batch_keys[last_index].append(task_key)

                        return

                    tasks_batch[last_index].append(_task_handler)

                    tasks_batch_keys[last_index].append(task_key)

                try:
                    obj = tasks_batch[last_index]

                    if len(obj) > 5:
                        last_index = last_index + 1
                        tasks_batch.append([])
                        tasks_batch_keys.append([])
                        repeats_batch.append([])
                        repeats_batch_keys.append([])
                        last_priority_tasks_batch.append([])
                        last_priority_tasks_batch_keys.append([])

                except IndexError:
                    tasks_batch.append([])
                    tasks_batch_keys.append([])
                    repeats_batch.append([])
                    repeats_batch_keys.append([])
                    last_priority_tasks_batch.append([])
                    last_priority_tasks_batch_keys.append([])

                handler_module = '/'.join([task.module, task.method])
                if handler_module in self.methods_object:
                    append_task(task, self.methods_object[handler_module])

                    if can_repeat_task and not task.is_last_priority:
                        repeats_batch[last_index].append(task_handler(task, self))
                        repeats_batch_keys[last_index].append(task.storage_data()[0])

            for tasks in tasks_batch:
                try:
                    await self.get_async_tasks(tasks)
                except uasyncio.CancelledError:
                    pass
                except Exception as e:
                    tasks_writer('Loop error: ' + str(e))

            for repeat_batch in repeats_batch:
                try:
                    await self.get_async_tasks(repeat_batch)
                except uasyncio.CancelledError:
                    pass
                except Exception as e:
                    tasks_writer('Repeats error: ' + str(e))

            for last_tasks in last_priority_tasks_batch:
                try:
                    await self.get_async_tasks(last_tasks)
                except uasyncio.CancelledError:
                    pass
                except Exception as e:
                    tasks_writer('Last error: ' + str(e))


tasks_instance = Tasks()
