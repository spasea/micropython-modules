# Station module usage

```python
from station import Station


wlan = Station("ssid", "password")
print('http://' + wlan.station.ifconfig()[0])
```