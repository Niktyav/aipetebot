import telebot
import os
from telebot import types

# Создаем бота
bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))


# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Если юзер прислал 1, выдаем ему случайный факт
    if '@aipeteBot' in message.text.strip():
            answer = 'я вас внимательно слушаю, вы сказали '+ message.text
            # Отсылаем юзеру сообщение в его чат
            bot.send_message(message.chat.id, answer)
    # Если юзер прислал 2, выдаем умную мысль
    elif message.text.strip() == 'Картинку':
        photo1 = open('test.jpg', 'rb')
        bot.send_photo(message.chat.id, photo1)
    else:
        bot.send_message(message.chat.id, 'моя твоя не понимать обратись ко мне')
# Запускаем бота
bot.polling(none_stop=True, interval=0)