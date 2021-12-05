# Logger module usage

```python
from logger import write, write_error, get_logs


# Writes to /log.txt file
write('Error here')

# Writes to /extra-log.txt file
write_error('Specific error', './extra-log.txt')

# Gets contents of the file
get_logs('./log.txt')
```