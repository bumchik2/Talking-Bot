import telebot
import config
import subprocess
from gtts import gTTS
import os
import json
import tests
import sys
from flask import Flask, request


from speech_recognizing import recognize_speech
from translator import translate

import elisa_reply
import smart_reply


def debug_function(func):
    def wrapper(*args, **kwargs):
        print(func.__name__, ' is called!', file=sys.stderr)
        return func(*args, **kwargs)

    return wrapper


class BotManager:
    help_message = """
Hello there, my name is Tommy! 
I can talk to you when you feel alone or just send you some useful info.
I can tell you about famous people, countries, musical groups and many other things.
Write me anything to start the conversation!

Use the following commands to manage chat settings:

/reply_language you can choose between English / Russian bot messages
/reply_type you can choose between audio / text bot messages
"""

    bot = telebot.TeleBot(config.TOKEN)
    bot_voice_enabled = False
    bot_language = 'en-US'
    waiting_for_command_reply = False

    @staticmethod
    @debug_function
    def convert_oga_to_wav(downloaded_file, filename_oga, filename_wav):
        with open(filename_oga, 'wb') as new_file:
            new_file.write(downloaded_file)

        process = subprocess.run(['ffmpeg', '-i', filename_oga, filename_wav])
        if process.returncode != 0:
            raise Exception("Something went wrong...")

    @staticmethod
    @debug_function
    def get_audio_from_text(text, filename_mp3):
        lang = 'ru' if BotManager.bot_language == 'ru-RU' else BotManager.bot_language
        output = gTTS(text=text, lang=lang, slow=False)
        output.save(filename_mp3)

    @staticmethod
    @debug_function
    def get_reply(user_message):
        smart_answer = smart_reply.get_reply(user_message, language=BotManager.bot_language)
        answer = smart_answer if smart_answer is not None else elisa_reply.get_reply(user_message)

        if BotManager.bot_language == 'ru-RU':
            answer = translate(answer, source_language='en', destination_language='ru')

        return answer

    @staticmethod
    @debug_function
    def reply(chat_id, user_message, voice_enable):
        if user_message == '':
            BotManager.bot.send_message(chat_id, 'Have you actually said something?')
            return

        reply_message = BotManager.get_reply(user_message)

        if voice_enable:
            filename_mp3 = 'reply.mp3'
            BotManager.get_audio_from_text(reply_message, filename_mp3)
            BotManager.bot.send_audio(chat_id, audio=open(filename_mp3, 'rb'))
            os.remove(filename_mp3)
        else:
            BotManager.bot.send_message(chat_id, reply_message)

    @staticmethod
    @debug_function
    def reply_to_command(message):
        if message.text == '/help' or message.text == '/start':
            BotManager.bot.send_message(message.chat.id, BotManager.help_message)

        elif message.text == '/reply_language':
            BotManager.waiting_for_command_reply = True
            BotManager.bot.send_message(chat_id=message.chat.id, text='Choose your language!',
                                        reply_markup=json.dumps({'keyboard': [['Russian'], ['English']],
                                                                 'one_time_keyboard': True}))

        elif message.text == '/reply_type':
            BotManager.waiting_for_command_reply = True
            BotManager.bot.send_message(chat_id=message.chat.id, text='Choose the type of messages you want to get!',
                                        reply_markup=json.dumps({'keyboard': [['Audio'], ['Text']],
                                                                 'one_time_keyboard': True}))

        else:
            BotManager.bot.send_message(chat_id=message.chat.id, text="Unknown command")

    @staticmethod
    @debug_function
    def get_command_reply(message):
        print('OK I am here!')
        BotManager.waiting_for_command_reply = False
        if message.text == 'Russian':
            print('OK you are choosing Russian!')
            BotManager.bot.send_message(message.chat.id, 'OK let\'s speak Russian!')
            BotManager.bot_language = 'ru-RU'
        elif message.text == 'English':
            print('OK you are choosing English!')
            BotManager.bot.send_message(message.chat.id, 'OK let\'s speak English!')
            BotManager.bot_language = 'en-US'
        elif message.text == 'Audio':
            print('OK you are choosing Audio!')
            BotManager.bot_voice_enabled = True
        elif message.text == 'Text':
            print('OK you are choosing Text!')
            BotManager.bot_voice_enabled = False
        else:
            BotManager.bot.send_message(message.chat.id, 'I am sorry, something went wrong...')
            return
        BotManager.bot.send_message(message.chat.id, 'New settings have been set successfully!')

    @staticmethod
    @bot.message_handler(content_types=['text'])
    @debug_function
    def reply_to_text_message(message):
        if BotManager.waiting_for_command_reply:
            BotManager.get_command_reply(message)
            return
        if message.text.startswith('/'):
            BotManager.reply_to_command(message)
        else:
            BotManager.reply(message.chat.id, message.text, voice_enable=BotManager.bot_voice_enabled)

    @staticmethod
    @bot.message_handler(content_types=['voice'])
    @debug_function
    def reply_to_voice(message):
        file_info = BotManager.bot.get_file(message.voice.file_id)
        downloaded_file = BotManager.bot.download_file(file_info.file_path)

        filename = str(message.voice.file_id)
        filename_oga = filename + '.oga'
        filename_wav = filename + '.wav'

        BotManager.convert_oga_to_wav(downloaded_file, filename_oga, filename_wav)

        user_message = recognize_speech(filename_wav, BotManager.bot_language)
        BotManager.bot.send_message(message.chat.id, 'I think you said: ' + user_message)

        BotManager.reply(message.chat.id, user_message, voice_enable=BotManager.bot_voice_enabled)

        os.remove(filename_oga)
        os.remove(filename_wav)


if __name__ == '__main__':
    tests.test_all()

    if "HEROKU" in list(os.environ.keys()):
        # logger = telebot.logger
        # telebot.logger.setLevel(logging.INFO)

        server = Flask(__name__)


        @server.route("/bot", methods=['POST'])
        def getMessage():
            BotManager.bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
            return "!", 200


        @server.route("/")
        def webhook():
            BotManager.bot.remove_webhook()
            BotManager.bot.set_webhook(
                url="https://min-gallows.herokuapp.com/bot")  # этот url нужно заменить на url вашего Хероку приложения
            return "?", 200


        server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
    else:
        # если переменной окружения HEROKU нету, значит это запуск с машины разработчика.
        # Удаляем вебхук на всякий случай, и запускаем с обычным поллингом.
        BotManager.bot.polling(none_stop=True)
