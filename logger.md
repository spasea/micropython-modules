# Logger module usage

```python
import logger


# Writes to /log.txt file
logger.write('Error here')

# Writes to /extra-log.txt file
logger.write_to_file('Specific error', './extra-log.txt')

# Gets logs path
logger.get_logs('./log.txt')

# Gets logs content
logger.read_logs('./log.txt')

# Add a logs formatter with time from last call
tasks_writer = logger.writer('Tasks')
tasks_writer('exception here')
```