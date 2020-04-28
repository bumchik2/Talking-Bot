from telegram_bot import BotManager
from tests import test_all


def run_bot():
    BotManager.bot.polling(none_stop=True)


def main():
    test_all()
    run_bot()


if __name__ == '__main__':
    main()
