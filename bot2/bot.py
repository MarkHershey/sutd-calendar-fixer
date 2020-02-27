import logging
import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
)
from datetime import datetime
import icsFixer
from config import CONFIG

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def timestamp():
    now = str(datetime.now())
    ts = ""
    for i in now[:-7]:
        if i in (" ", "-", ":"):
            pass
        else:
            ts += i
    return ts


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context):
    msg = """
Howdy {},

Send me your schedule in `.ics`, I will make it look *prettier*!

First time here? Use /help

/help : check how to download your schedule.

/friends : get to know my friends.

/source : view source / contribute.
""".format(
        update.message.chat.first_name
    )
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)


def help(update, context):
    msg = """
Do you know that you can import your class schedule into your Google Calendar?

You can download an importable `.ics` file from SUTD, but the original file is badly formatted and it won't look good on your calendar App.
This bot helps you clean up the mess in the `.ics` file so that you will get a neat calendar view.

Follow this step-by-step instruction:

1. Visit [mymobile.sutd.edu.sg](mymobile.sutd.edu.sg)
2. Choose `Student Log In` (a large green button)
3. Use your SUTD Network ID (100xxxx) and password to log in
4. Left-hand side menu (hamburger menu button) -> Choose `Schedule`z
5. Top-right gear-like button -> Choose `Download Schedule`
6. Select the term of schedule which you wish to download
7. You will get a `schedule.ics` file.

*Come back, send the file to me in this chat!*

"""
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)


def friends(update, context):
    msg = """
I have some bot friends at SUTD, check them out!

@SUTDMapBot tells you where your think tanks are (and more)!

@evs_notification_bot tells you about your air-con credits!

@shimekiribot keeps an eye on your due days.
"""
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)


def source(update, context):
    msg = "View source / contribute on [GitHub](https://github.com/MarkHershey/calendar-generator)"
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def ics(update, context):
    # get file type
    file_type = update.message.document.mime_type
    # proceed only if the file is an ics
    if file_type == "text/calendar":
        # update.message.reply_text("Received!", parse_mode=telegram.ParseMode.MARKDOWN)
        print("--- new ics received ---")
        ts = timestamp()
        file_id = update.message.document.file_id
        newFile = context.bot.get_file(file_id)
        newFile.download(f"{ts}.ics")
        # format the ics file
        new_file, number_of_events = icsFixer.fix(ts)
        # reply back
        update.message.reply_text(
            f"{number_of_events} events successfully re-formatted!",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        context.bot.send_document(
            chat_id=update.effective_chat.id, document=open(new_file, "rb")
        )
        update.message.reply_text(
            f"Now you can import this file into your Google/ Apple Calendar.",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )

    else:
        update.message.reply_text(
            "I can only digest `.ics` file for now.",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )


def main():
    """Start the bot"""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(CONFIG["bot_token"], use_context=True)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Command Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("friends", friends))
    dispatcher.add_handler(CommandHandler("source", source))

    # Message Handlers
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    dispatcher.add_handler(MessageHandler(Filters.document, ics))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
