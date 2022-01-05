import utime
import json
import random
import uasyncio
import sys

from .chat import Message
from .logger import writer

mqtt_writer = writer('MQTT', './mqtt.txt')


def random_float(min_num, max_num):
    return random.random() * (max_num - min_num) + min_num


class TGMqtt:
    def __init__(self, sub_chat: Message, pub_chat: Message, limit: int = 100):
        self.id = random_float(1, 10000)
        self.sub = sub_chat
        self.pub = pub_chat
        self.topics = {}
        self.update_ids = {}
        self.last_update = -1
        self.limit = limit
        self.waiting_time = round(random_float(0.5, 2) * 1000)

    async def publish(self, topic: str, data: dict or None = None, text: str = '', reply_id: int or None = None):
        if data is None:
            data = {}
        data = json.dumps({
            'data': data,
            'topic': topic,
            'text': text,
            'reply_id': reply_id,
            'publisher': self.id,
        })

        self.pub.send_message(data)

    def parse_update(self, update: dict) -> dict:
        try:
            content_json = json.loads(update['channel_post']['text'])

            content = {
                "text": content_json['text'] if 'text' in content_json else '',
                "topic": content_json['topic'] if 'topic' in content_json else '',
                "reply_id": content_json['reply_id'] if 'reply_id' in content_json else None,
                "data": content_json['data'] if 'data' in content_json else {},
                "publisher": content_json['publisher'] if 'publisher' in content_json else 0,
                "update_id": update["update_id"],
                "id": update["channel_post"]["message_id"],
                "update_time": update["channel_post"]["date"],
                "message_id": update["channel_post"]["message_id"],
            }

            del content_json
        except Exception as e:
            sys.print_exception(e)
            content = {"data": {}, "topic": "", "update_id": 0, "update_time": 0, "publisher": 0,
                       "text": update['channel_post']['text'], "reply_id": None,
                       "id": update['channel_post']['message_id']}

        return content

    # async callback with update as argument
    def subscribe_to_topic(self, topic: str, callback):
        self.topics[topic] = callback

        return self

    def unsubscribe_from_topic(self, topic: str):
        if topic not in self.topics:
            return self

        del self.topics[topic]

        return self

    async def subscribe(self, task):
        utime.sleep_ms(self.waiting_time)

        try:
            res = self.sub.get_updates(self.last_update, ["channel_post"])
            updates = res['result']

            if len(updates) == self.limit:
                self.last_update = updates[round(self.limit * 0.2) - 1]['update_id']

                return

            messages = []
            max_messages_in_batch = 5
            messages_batch_idx = 0

            for update in updates:
                if not str(update['channel_post']['chat']['id']) == self.sub.chat_id:
                    continue

                if self.last_update == -1:
                    self.last_update = update['update_id']

                parsed_message = self.parse_update(update)

                if parsed_message['topic'] not in self.topics or \
                        parsed_message['update_id'] in self.update_ids or \
                        (str(parsed_message['publisher']) == str(self.id) and not parsed_message['topic'].startswith('service')):
                    continue

                try:
                    element = messages[messages_batch_idx]

                    if len(element) > max_messages_in_batch:
                        messages_batch_idx += 1
                        messages.append([])
                except IndexError:
                    messages.append([])

                self.update_ids[parsed_message['update_id']] = ''
                messages[messages_batch_idx].append(
                    uasyncio.create_task(self.topics[parsed_message['topic']](parsed_message)))

            for messages_batch in messages:
                try:
                    await uasyncio.gather(*messages_batch)
                except uasyncio.CancelledError:
                    pass
                except Exception as e:
                    sys.print_exception(e)
                    mqtt_writer('MQTT topics execution - ' + str(e))

        except Exception as e:
            sys.print_exception(e)
            mqtt_writer('request e ' + str(e))
