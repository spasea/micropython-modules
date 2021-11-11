# Station module usage

```python
from station import Station


wlan = Station("ssid", "password")
print('http://' + wlan.station.ifconfig()[0])
```

### Also the list of networks can be passed

```python
from station import Station


wlan = Station(single_string="ssid__password____ssid1__password1")
print('http://' + wlan.station.ifconfig()[0])
```