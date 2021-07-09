# API module usage

```python
from api import Rest


def pin_handler(path):
    arguments = path.split('/')

    if len(arguments) < 2:
        return {'key': 'no pin presented'}

    pin = arguments[2].strip()

    return {'key': pin}


def status_handler(path):
    return {'key': 'status ok'}


instance = Rest()
instance.subscribe('/pin/.+', pin_handler)
instance.subscribe('/status', status_handler)
instance.listen()
```