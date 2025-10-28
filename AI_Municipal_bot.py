from telebot import TeleBot
from telebot.types import Update, Message
import os
from dotenv import load_dotenv
from flask import Flask, request, abort

load_dotenv()

TOKEN = os.getenv('TOKEN')
TARGET_CHAT_ID = int(os.getenv('TARGET_CHAT_ID'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

bot = TeleBot(TOKEN)
app = Flask(__name__)

PROJECT_INFO = """
Отправьте /send чтобы поделиться кейсом.

Отправьте /share чтобы прикрепить вложения.
"""

COORDINATOR_CONTACTS = """
Координатор @Marina_Ekba

Телефон: +7(926)931-96-60
"""

SEND_REPLY_MESSAGE = """
Отправьте описание решения (одно сообщение).

В описании укажите:

1. Решаемую задачу и использованный инструмент ИИ.

2. Достигнутый результат (какие задачи были успешно выполнены) или укажите какие проблемы возникли.

3. Ваши контакты для возможного взаимодействия.
"""

SHARE_REPLY_MESSAGE = """
Отправьте вложения (фото/документ/видео — одно сообщение).
"""

user_states = {}

def process_message(message: Message):
    user_id = message.from_user.id

    if message.text.startswith('/'):
        if user_states.get(user_id):
            del user_states[user_id]

        if message.text == '/start':
            bot.send_message(message.chat.id, PROJECT_INFO)
        elif message.text == '/contacts':
            bot.send_message(message.chat.id, COORDINATOR_CONTACTS)
        elif message.text == '/send':
            bot.send_message(message.chat.id, SEND_REPLY_MESSAGE)
            user_states[user_id] = {'state': 'send'}
        elif message.text == '/share':
            bot.send_message(message.chat.id, SHARE_REPLY_MESSAGE)
            user_states[user_id] = {'state': 'share'}
    else:
        state = user_states.get(user_id)
        if not state:
            return

        if state['state'] == 'send':
            if message.text and not message.text.startswith('/'):
                bot.forward_message(TARGET_CHAT_ID, message.chat.id, message.message_id)
                bot.send_message(message.chat.id, "Описание решения отправлено.")
            else:
                bot.send_message(message.chat.id, "Пожалуйста отправьте только текстовое сообщение.")
                return
        elif state['state'] == 'share':
            if message.photo or message.document or message.video:
                bot.forward_message(TARGET_CHAT_ID, message.chat.id, message.message_id)
                bot.send_message(message.chat.id, "Вложения отправлены.")
            else:
                bot.send_message(message.chat.id, "Пожалуйста отправьте только фото, документ или видео.")
                return

        del user_states[user_id]

@bot.message_handler(func=lambda m: True)
def handle_all(message: Message):
    process_message(message)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_data = request.get_json()
        update = Update.de_json(json_data, bot)
        bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)

@app.route('/')
def index():
    return 'Bot is running'

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))