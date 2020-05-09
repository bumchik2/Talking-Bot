# used for running on PC

from telegram_bot import BotManager
from tests import test_all
import warnings

warnings.filterwarnings("ignore")


def run_bot():
    BotManager.bot.delete_webhook()
    BotManager.bot.polling(none_stop=True)


def main():
    test_all()
    run_bot()


if __name__ == '__main__':
    main()
