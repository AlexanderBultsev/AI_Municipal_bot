import os
from flask import Flask, request
from telebot import TeleBot
from telebot.types import Message, Update
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

app = Flask(__name__)
bot = TeleBot(os.getenv('TOKEN'))
TOKEN = os.getenv('TOKEN')
TARGET_CHAT_ID = int(os.getenv('TARGET_CHAT_ID'))

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
    if message.text and not message.text.startswith('/'):
        bot.forward_message(TARGET_CHAT_ID, message.chat.id, message.message_id)
        bot.reply_to(message, "Решение отправлено.")
    else:
        bot.reply_to(message, "Пожалуйста отправьте только текстовое сообщение.")

@bot.message_handler(commands=['share'])
def handle_share(message: Message):
    bot.reply_to(message, "Отправьте вложения (документ/фото/видео — одно сообщение).")
    bot.register_next_step_handler(message, forward_attachment)

def forward_attachment(message: Message):
    if message.photo or message.document or message.video:
        bot.forward_message(TARGET_CHAT_ID, message.chat.id, message.message_id)
        bot.reply_to(message, "Вложения отправлены.")
    else:
        bot.reply_to(message, "Пожалуйста отправьте только документ, фото или видео.")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    else:
        return "Unauthorized."

@app.route("/")
def health_check():
    return "OK"

def run_bot():
    bot.remove_webhook()
    # bot.set_webhook(url=f"https://ai-municipal-bot.onrender.com/{TOKEN}")
    bot.infinity_polling(none_stop=True, interval=0)

if __name__ == "__main__":
    t = Thread(target=run_bot)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)