import utime
import uasyncio

from .chat import Message
from .tasks import Tasks
from .tg_mqtt import TGMqtt


def run(_handler, config, _tasks_handler=None, _config_mqtt_chat='mqtt_chat', _config_mqtt_sub='mqtt_sub',
        _config_mqtt_pub='mqtt_pub'):
    loop = uasyncio.new_event_loop()

    def handler():
        return 1

    mqtt_instance = TGMqtt(Message(config[_config_mqtt_chat], config[_config_mqtt_sub]),
                           Message(config[_config_mqtt_chat], config[_config_mqtt_pub]))
    tasks_instance = Tasks(_tasks_handler or handler)

    client_tasks = _handler(tasks_instance, mqtt_instance)

    tasks_instance.add_method('check', 'mqtt', mqtt_instance.subscribe)
    now_time = utime.time()

    # now time + year seconds
    tasks_instance.add_task('check', 'mqtt', now_time, now_time + 525600, 0, {})

    loop.run_until_complete(uasyncio.gather(tasks_instance.main(), *client_tasks))
