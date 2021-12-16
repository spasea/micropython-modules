# Tasks via mqtt module usage

```python
import uasyncio
from tasks_via_mqtt import run as run_tasks


async def test_message(message):
    print('Test - ' + str(message['data']) + '; ' + str(message['text']))

async def ready():
    print('ready')
    
def handler(tasks_instance, mqtt_instance):
    mqtt_instance.subscribe_to_topic('test:message', test_message)
    
    return [
        uasyncio.create_task(ready())
    ]

run_tasks(handler, {})
```