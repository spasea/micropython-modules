# Server module usage

```python
import server as tinyweb
import utime
import uasyncio


class Temperature:
    def get(self, data):
        [temp, hum, real_feel] = [10, 20, 30]

        return {"humidity": hum, "temperature": temp, "real_feel": real_feel}

def main():
    app = tinyweb.webserver(backlog=30, debug=True)

    @app.route('/')
    async def index(request, response):
        # Start HTTP response with content-type text/html
        await response.start_html()
        # Send actual HTML page
        await response.send('<html><head><title>Logs</title></head><body><div>Server time: ' + str(utime.time()) + '</div></body></html>'

    app.add_resource(Temperature(), '/temperature')

    return app.run(host="0.0.0.0", port=8081, loop_forever=False)


def run():
    loop = uasyncio.new_event_loop()

    def handler(_loop, context):
        _loop.stop()
        run()

    loop.set_exception_handler(handler)

    loop.run_until_complete(
        uasyncio.gather(
            # Other tasks
            main(), 
            return_exceptions=True
        )
    )


# In main file start handler
run()
```