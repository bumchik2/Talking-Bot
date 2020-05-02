import telebot
import config
import subprocess
from gtts import gTTS
import os
import json
import sys


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
    default_voice_enabled = False
    default_language = 'en-US'
    default_waiting_for_command_reply = False

    id_voice_enabled = dict()
    id_languages = dict()
    id_waiting_for_reply = dict()

    @staticmethod
    def init_user(chat_id):
        BotManager.id_voice_enabled[chat_id] = BotManager.default_voice_enabled
        BotManager.id_languages[chat_id] = BotManager.default_language
        BotManager.id_waiting_for_reply[chat_id] = BotManager.default_waiting_for_command_reply

    @staticmethod
    def init_chat_if_needed(chat_id):
        if chat_id not in BotManager.id_languages:
            BotManager.init_user(chat_id)

    @staticmethod
    def convert_oga_to_wav(downloaded_file, filename_oga, filename_wav):
        with open(filename_oga, 'wb') as new_file:
            new_file.write(downloaded_file)

        process = subprocess.run(['ffmpeg', '-i', filename_oga, filename_wav])
        if process.returncode != 0:
            raise Exception("Something went wrong...")

    @staticmethod
    def get_audio_from_text(text, filename_mp3, language):
        lang = 'ru' if language == 'ru-RU' else language
        output = gTTS(text=text, lang=lang, slow=False)
        output.save(filename_mp3)

    @staticmethod
    def get_reply(user_message, chat_id):
        smart_answer = smart_reply.get_reply(user_message, language=BotManager.id_languages[chat_id])
        answer = smart_answer if smart_answer is not None else elisa_reply.get_reply(user_message)

        if BotManager.id_languages[chat_id] == 'ru-RU':
            answer = translate(answer, source_language='en', destination_language='ru')

        return answer

    @staticmethod
    def reply(chat_id, user_message):
        if user_message == '':
            BotManager.bot.send_message(chat_id, 'Have you actually said something?')
            return

        reply_message = BotManager.get_reply(user_message, chat_id)
        print('Bot: ', reply_message, file=sys.stderr)

        if BotManager.id_voice_enabled[chat_id]:
            filename_mp3 = 'reply.mp3'
            BotManager.get_audio_from_text(reply_message, filename_mp3, language=BotManager.id_languages[chat_id])
            BotManager.bot.send_audio(chat_id, audio=open(filename_mp3, 'rb'))
            os.remove(filename_mp3)
        else:
            BotManager.bot.send_message(chat_id, reply_message)

    @staticmethod
    def reply_to_command(message):
        if message.text == '/start':
            BotManager.init_user(message.chat.id)
        if message.text == '/help' or message.text == '/start':
            BotManager.bot.send_message(message.chat.id, BotManager.help_message)
        elif message.text == '/reply_language':
            BotManager.id_waiting_for_reply[message.chat.id] = True
            BotManager.bot.send_message(chat_id=message.chat.id, text='Choose your language!',
                                        reply_markup=json.dumps({'keyboard': [['Russian'], ['English']],
                                                                 'one_time_keyboard': True}))
        elif message.text == '/reply_type':
            BotManager.id_waiting_for_reply[message.chat.id] = True
            BotManager.bot.send_message(chat_id=message.chat.id, text='Choose the type of messages you want to get!',
                                        reply_markup=json.dumps({'keyboard': [['Audio'], ['Text']],
                                                                 'one_time_keyboard': True}))
        else:
            BotManager.bot.send_message(chat_id=message.chat.id, text="Unknown command")

    @staticmethod
    def get_command_reply(message):
        BotManager.id_waiting_for_reply[message.chat.id] = False
        bot_reply = 'Oops, looks like something went wrong...'

        if message.text == 'Russian':
            BotManager.id_languages[message.chat.id] = 'ru-RU'
            bot_reply = 'Отлично, давай поговорим на русском!'
        elif message.text == 'English':
            BotManager.id_languages[message.chat.id] = 'en-US'
            bot_reply = 'OK let\'s speak English!'
        elif message.text == 'Audio':
            BotManager.id_voice_enabled[message.chat.id] = True
            bot_reply = 'New settings have been set successfully!'
        elif message.text == 'Text':
            BotManager.id_voice_enabled[message.chat.id] = False
            bot_reply = 'New settings have been set successfully!'
        else:
            pass

        print('Bot: ', bot_reply, file=sys.stderr)
        BotManager.bot.send_message(message.chat.id, bot_reply)

    @staticmethod
    @bot.message_handler(content_types=['text'])
    def reply_to_text_message(message):
        BotManager.init_chat_if_needed(message.chat.id)
        print('User id =', message.chat.id, ':', message.text, file=sys.stderr)

        if BotManager.id_waiting_for_reply[message.chat.id]:
            BotManager.get_command_reply(message)
            return
        if message.text.startswith('/'):
            BotManager.reply_to_command(message)
        else:
            BotManager.reply(message.chat.id, message.text)

    @staticmethod
    @bot.message_handler(content_types=['voice'])
    def reply_to_voice(message):
        BotManager.init_chat_if_needed(message.chat.id)

        file_info = BotManager.bot.get_file(message.voice.file_id)
        downloaded_file = BotManager.bot.download_file(file_info.file_path)

        filename = str(message.voice.file_id)
        filename_oga = filename + '.oga'
        filename_wav = filename + '.wav'

        BotManager.convert_oga_to_wav(downloaded_file, filename_oga, filename_wav)

        user_message = recognize_speech(filename_wav, BotManager.id_languages[message.chat.id])
        BotManager.bot.send_message(message.chat.id, 'I think you said: ' + user_message)

        BotManager.reply(message.chat.id, user_message)

        os.remove(filename_oga)
        os.remove(filename_wav)
