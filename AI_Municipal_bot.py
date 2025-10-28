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
Отправьте вложение (один документ/фото/видео).
"""

@bot.message_handler(commands=['start'])
def handle_about(message: Message):
    bot.reply_to(message, PROJECT_INFO)

@bot.message_handler(commands=['contacts'])
def handle_contacts(message: Message):
    bot.reply_to(message, COORDINATOR_CONTACTS)

@bot.message_handler(commands=['send'])
def handle_send(message: Message):
    bot.reply_to(message, SEND_REPLY_MESSAGE)
    bot.register_next_step_handler(message, forward_text_solution)

def forward_text_solution(message: Message):
    if message.text and (message.text[0] != '/'):
        bot.forward_message(TARGET_CHAT_ID, message.chat.id, message.message_id)
        bot.reply_to(message, "Решение отправлено.")
    else:
        bot.reply_to(message, "Пожалуйста отправьте только текстовое сообщение.")

@bot.message_handler(commands=['share'])
def handle_share(message: Message):
    bot.reply_to(message, SHARE_REPLY_MESSAGE)
    bot.register_next_step_handler(message, forward_attachment)

def forward_attachment(message: Message):
    if  message.photo or message.document or message.video:
        bot.forward_message(TARGET_CHAT_ID, message.chat.id, message.message_id)
        bot.reply_to(message, "Вложение отправлено.")
    else:
        bot.reply_to(message, "Пожалуйста отправьте только один документ, фото или видео.")


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
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