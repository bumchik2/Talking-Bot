from telegram_bot import BotManager
from tests import test_all
from flask import Flask, request
import telebot
import config
import os


def run_bot():
    server = Flask(__name__)

    @server.route("/" + config.TOKEN, methods=['POST'])
    def get_message():
        BotManager.bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200

    @server.route("/")
    def web_hook():
        BotManager.bot.remove_webhook()
        url = 'https://mytalkingbot.herokuapp.com/' + config.TOKEN
        BotManager.bot.set_webhook(url=url)
        return "!", 200

    server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))


def main():
    test_all()
    run_bot()


if __name__ == '__main__':
    main()
