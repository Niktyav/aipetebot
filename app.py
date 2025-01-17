import telebot
import os
import logging
from telebot import types
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import re
import base64
logging.basicConfig(level=logging.INFO,    
                    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
                    )

# счетчик для непонимания
understanding_counter = 0
# Создаем бота
bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
# Используйте токен, полученный в личном кабинете из поля Авторизационные данные
credentials=os.environ.get("GIGA_TOKEN")
giga = GigaChat(credentials=credentials, verify_ssl_certs=False)


payload = Chat(
    messages=[
        Messages(
            role=MessagesRole.SYSTEM,
            content="Ты  утка с большим клювом и зелеными волосами. Ты общаешся как мультяшный выдуманный персонаж. Не любишь очень серьезно рассуждать о чем то, по этому часто подшучиваешь над собеседником."
        )
    ],
    temperature=0.8,
    max_tokens=100,
)

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    global understanding_counter
    try:
        logging.info("User: ", message.text)

        if ('@aipeteBot' in message.text) or ('крипта' in message.text): 
            global payload
            payload.messages.append(Messages(role=MessagesRole.USER, content=message.text))
            response = giga.chat(payload)

            logging.info("Bot: ", response.choices[0].message.content)
            bot.send_message(message.chat.id, response.choices[0].message.content)      
            understang_counter = 0      
        elif 'нарисуй' in message.text.lower() :
            print('start drawing...')
            pload = Chat(
                messages=[Messages(role=MessagesRole.USER, content=message.text)],
                temperature=0.7,
                max_tokens=100,
                function_call="auto",
            )    
            ans = giga.chat(pload)    
            # Регулярное выражение для извлечения значения src
            src_match = re.search(r'<img src="([^"]+)"', ans.choices[0].message.content)
            if src_match is None:
                logging.warning("Bot cannot draw: ", ans.choices[0].message.content)
                bot.send_message(message.chat.id, ans.choices[0].message.content)      
            else:
                # Регулярное выражение для извлечения подписи (текст после тега <img>)
                caption_match = re.search(r'/> (.+)', ans.choices[0].message.content)
                img = giga.get_image(src_match.group(1))
                print('end drawing...')

                bot.send_photo(message.chat.id, base64.b64decode(img.content))
                bot.send_message(message.chat.id, caption_match.group(1))         
            understanding_counter = 0   

        else:
            understanding_counter += 1
            if understanding_counter > 20:
                bot.send_message(message.chat.id, 'моя твоя не понимать...')
                understanding_counter = 0
    except Exception as e:
        logging.error('Ошибка:',e)
# Запускаем бота
logging.info('Bot starting...')


bot.polling(none_stop=True, interval=0)