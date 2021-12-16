import urequests


class Message:
    def __init__(self, chat_id: str, bot_id: str):
        self.bot_id = bot_id
        self.chat_id = chat_id

    def send_message(self, message: str) -> dict:
        url = 'https://api.telegram.org/bot' + str(self.bot_id) + '/sendMessage?chat_id=' + str(
            self.chat_id) + '&text=' + message

        response = urequests.get(url)
        return response.json()

    def get_updates(self, offset: int, updates: list = None, timeout: int = 0) -> dict:
        if updates is None:
            updates = []

        url = 'https://api.telegram.org/bot' + str(self.bot_id) + '/getUpdates?offset=' + str(
            offset) + '&allowed_updates=' + str(updates) + '&timeout=' + str(timeout)

        response = urequests.get(url)

        return response.json()
