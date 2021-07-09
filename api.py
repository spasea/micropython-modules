import socket
import json
import re


class Rest:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.routes = {}

    def subscribe(self, route, callback):
        self.routes[route] = callback

        return self

    def process_connection(self, connection, _dict):
        connection.send('HTTP/1.1 200 OK\n')
        connection.send('Content-Type: application/json\n')
        connection.send('Connection: close\n\n')

        connection.sendall(json.dumps(_dict))
        connection.close()

    def listen(self):
        self.s.bind(('', 80))
        self.s.listen(3)

        while True:
            connection, address = self.s.accept()
            request = str(connection.recv(1024))

            path = request.split(' ')[1] + ' '
            is_exact_match = path in self.routes

            message = {}

            if is_exact_match:
                self.process_connection(connection, self.routes[path](path))

                continue

            for route in self.routes:
                is_route_similar = re.match(route, path)

                if not is_route_similar:
                    continue

                message = self.routes[route](path)

                break

            self.process_connection(connection, message)
