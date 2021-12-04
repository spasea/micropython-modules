# Tasks module usage

```python
from tasks import Tasks
import uasyncio

# Initialization goes in your main method
def init_handler():
    print('Tasks loop initialized')

tasks_instance = Tasks(init_handler)
loop = uasyncio.new_event_loop() # or uasyncio.get_event_loop()
loop.run_until_complete(
    uasyncio.gather(
        # other tasks
        loop.create_task(tasks_instance.main())
    )
)

# Registering task
async def number_print_handler(_payload):
    print(float(_payload['next_number']))
    
tasks_instance.add_method('print', 'number', number_print_handler)

# Adding task to be run 
# now time is 100
tasks_instance.add_task('print', 'number', 115, 200, 15, {
    'next_number': 12
})
# Then this task will be executed until server time will be 200 or greater
```