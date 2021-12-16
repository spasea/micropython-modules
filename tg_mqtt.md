# Tasks module usage

```python
import uasyncio
from tg_mqtt import TGMqtt
from chat import Message


# Basic init
mqtt_instance = TGMqtt(Message('123456', 'sub_id'),
                       Message('123456', 'pub_id'))

async def test_message(message):
    print('Test - ' + str(message['data']) + '; ' + str(message['text']))

mqtt_instance.subscribe_to_topic('test:message', test_message)

async def mqtt_main():
    while True:
        await mqtt_instance.subscribe({})

loop = uasyncio.new_event_loop()
loop.run_until_complete(mqtt_main())

# Publish messages with data
mqtt_instance.publish({
    'test': 123
}, 'test:data')

# or with plain text
mqtt_instance.publish({}, 'test:text', 'Text here')
```