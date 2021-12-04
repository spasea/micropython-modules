# Logger module usage

```python
from logger import write, write_error


# Writes to /log.txt file
write('Error here')

# Writes to /extra-log.txt file
write_error('Specific error', './extra-log.txt')
```