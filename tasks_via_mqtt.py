import json

import utime
import uasyncio
import machine
import sys

from .chat import Message
from .state_save import StateSaveInterface
from .tasks import tasks_instance
from .tg_mqtt import TGMqtt


def run(_sensor_mqtt_tasks_handler, _sensor_state: StateSaveInterface, config, _config_mqtt_chat='mqtt_chat',
        _config_mqtt_sub='mqtt_sub',
        _config_mqtt_pub='mqtt_pub', __id=None, _limit=40):
    loop = uasyncio.new_event_loop()

    mqtt_instance = TGMqtt(Message(config[_config_mqtt_chat], config[_config_mqtt_sub]),
                           Message(config[_config_mqtt_chat], config[_config_mqtt_pub]), _id=__id, limit=_limit)

    now_time = utime.time()
    tasks_instance.add_method('check', 'mqtt', mqtt_instance.subscribe)

    try:
        with open('./app/general-config.json', 'r') as general_state_config_file:
            general_state_config = json.loads(general_state_config_file.read())

        tasks_instance.from_string(general_state_config['tasks'], general_state_config['time'])
    except Exception as e:
        general_state_config = {
            "sensor": "{}",
            "tasks": "{}",
            "time": machine.RTC().datetime()
        }

        tasks_instance.add_method('check', 'mqtt', mqtt_instance.subscribe)
        # now time + year seconds
        tasks_instance.add_task('check', 'mqtt', now_time, now_time + 525600, 0, {})

    machine.RTC().init(general_state_config['time'])
    _sensor_state.from_string(general_state_config['sensor'], general_state_config['time'])
    _sensor_mqtt_tasks_handler(mqtt_instance)

    async def reset_module(task):
        def handler():
            tasks_string = tasks_instance.to_string()
            sensor_string = _sensor_state.to_string()

            with open('./app/general-config.json', 'w') as file:
                file.write(json.dumps({
                    "sensor": sensor_string,
                    "tasks": tasks_string,
                    "time": machine.RTC().datetime()
                }))

            machine.reset()

        try:
            handler()
        except Exception as e:
            sys.print_exception(e)
            print(e)

    tasks_instance.add_method('reset', 'system', reset_module)
    # now time + 24h seconds
    tasks_instance.add_task('reset', 'system', now_time + 1440, now_time + 2440, 0, {})

    loop.run_until_complete(uasyncio.gather(tasks_instance.main()))
