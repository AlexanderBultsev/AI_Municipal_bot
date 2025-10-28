from telebot import TeleBot
from telebot.types import Message
import os
from dotenv import load_dotenv

load_dotenv()

bot = TeleBot(os.getenv('TOKEN'))

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
    if message.text and (message.text[0] != '/'):
        bot.forward_message(TARGET_CHAT_ID, message.chat.id, message.message_id)
        bot.reply_to(message, "Решение отправлено.")
    else:
        bot.reply_to(message, "Пожалуйста отправьте только текстовое сообщение.")
    

@bot.message_handler(commands=['share'])
def handle_share(message: Message):
    bot.reply_to(message, "Отправьте вложения (документ/фото/видео — одно сообщение).")
    bot.register_next_step_handler(message, forward_attachment)

def forward_attachment(message: Message):
    if  message.photo or message.document or message.video:
        bot.forward_message(TARGET_CHAT_ID, message.chat.id, message.message_id)
        bot.reply_to(message, "Вложения отправлены.")
    else:
        bot.reply_to(message, "Пожалуйста отправьте только документ, фото или видео.")

bot.infinity_polling()