import urequests


class Message:
    def __init__(self, chat_id, bot_id):
        self.bot_id = bot_id
        self.chat_id = chat_id

    def send_message(self, message):
        url = 'https://api.telegram.org/bot' + str(self.bot_id) + '/sendMessage?chat_id=' + str(
            self.chat_id) + '&text=' + message

        response = urequests.get(url)
        return response.json()

    def get_updates(self, offset, updates=None, timeout=0):
        if updates is None:
            updates = []

        url = 'https://api.telegram.org/bot' + str(self.bot_id) + '/getUpdates?offset=' + str(
            offset) + '&allowed_updates=' + str(updates) + '&timeout=' + str(timeout)

        response = urequests.get(url)

        return response.json()
