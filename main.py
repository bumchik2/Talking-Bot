from telegram_bot import BotManager
from tests import test_all
from flask import Flask, request
import telebot
import config
import os

server = Flask(__name__)


@server.route('/' + config.TOKEN, methods=['POST'])
def getMessage():
    print('getting message')
    BotManager.bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return '!', 200


@server.route('/')
def webhook():
    print('web hook is called')
    BotManager.bot.remove_webhook()
    url = 'https://peaceful-shelf-93340.herokuapp.com/' + config.TOKEN
    BotManager.bot.set_webhook(url=url)
    return '!', 200


def run_bot():
    print('running bot')
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


def main():
    print('main is called')
    test_all()
    run_bot()


if __name__ == '__main__':
    main()
