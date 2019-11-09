import logging
import os
import sys
import reader

from telegram import Update
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram.ext import CallbackContext, run_async

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
IMG_NAME = 'qr_image.png'

if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def start_handler(bot, update):
    # Creating a handler-function for /start command
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text("Hello from QReaderBot!\nSend me a QR Code")


@run_async
def decode(update: Update, context: CallbackContext):
    del context
    update.message.chat_id

    if update.message.photo:
        update.message.photo[-1].file_id
        photo = update.effective_message.photo[-1]
    else:
        return

    file = photo.get_file()
    file.download(IMG_NAME)
    result = reader.decode_and_select(IMG_NAME)

    try:
        update.effective_message.reply_text(result)
        os.remove(IMG_NAME)
    except Exception as e:
        update.effective_message.reply_text(str(e))


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, decode))

    run(updater)
