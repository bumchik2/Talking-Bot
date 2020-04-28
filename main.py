from telegram_bot import BotManager, debug_function
from tests import test_all
from flask import Flask, request
import telebot
import config
import os

server = Flask(__name__)


@server.route('/' + config.TOKEN, methods=['POST'])
@debug_function
def get_message():
    BotManager.bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return '!', 200


@server.route('/')
@debug_function
def web_hook():
    BotManager.bot.remove_webhook()
    url = 'https://peaceful-shelf-93340.herokuapp.com/' + config.TOKEN
    BotManager.bot.set_webhook(url=url)
    return '!', 200


@debug_function
def run_bot():
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


@debug_function
def main():
    test_all()
    run_bot()


if __name__ == '__main__':
    main()
