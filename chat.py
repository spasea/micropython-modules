import urequests


class Message:
    def __init__(self, chat_id, bot_id):
        self.bot_id = bot_id
        self.chat_id = chat_id

    def send_message(self, message):
        response = urequests.get('https://api.telegram.org/'
                                 + str(self.bot_id)
                                 + '/sendMessage?chat_id='
                                 + str(self.chat_id)
                                 + '&text=' + message)
        print(response.text)
