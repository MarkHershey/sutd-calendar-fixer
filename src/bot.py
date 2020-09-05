# built-in modules
import os
import json
from pathlib import Path
from datetime import datetime

# internal modules
import calendarFixer

# external modules
import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
)
from markkk.logger import logger

curr_folder: Path = Path(__file__).parent.resolve()
project_root: Path = curr_folder.parent
usr_data_path: Path = project_root / "usr_data"
logs_path: Path = project_root / "logs"

if not logs_path.is_dir():
    os.mkdir(str(logs_path))
if not usr_data_path.is_dir():
    os.mkdir(str(logs_path))


def timestamp_now() -> str:
    """ return a timestamp in string: YYYYMMDDHHMMSS"""
    now: str = str(datetime.now())
    ts: str = ""
    for i in now[:-7]:
        if i in (" ", "-", ":"):
            pass
        else:
            ts += i
    return ts


def user_log(update, ts: str = None, remarks: str = ""):
    if not ts:
        ts: str = timestamp_now()
    first_name: str = update.message.chat.first_name
    last_name: str = update.message.chat.last_name
    username: str = update.message.chat.username
    id: str = update.message.chat.id
    name: str = f"{first_name} {last_name}"
    record: str = f"{ts} - id({id}) - username({username}) - name({name}) - visited({remarks})\n"
    user_log_fp: Path = logs_path / "user_visit_history.txt"
    with user_log_fp.open(mode="a") as f:
        f.write(record)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')


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
    user_log(update, remarks="/start")


def help(update, context):
    msg = """
Do you know that you can import your class schedule into your Google Calendar?

You can download an importable `.ics` file from SUTD, but the original file is badly formatted and it won't look good on your calendar App.

This bot helps you clean up the mess in the `.ics` file so that you will get a neat calendar view.

Follow the step-by-step instructions to download your schedule, then *come back and send the file you downloaded to me (this chat)*.

1. Visit [https://mymobile.sutd.edu.sg/app/dashboard](https://mymobile.sutd.edu.sg/app/dashboard)
2. Use your SUTD Network ID (100xxxx) and password to log in
3. Left-hand side menu (hamburger menu button) -> Choose *Schedule*
4. Top-right gear-like button -> Choose *Download Schedule*

Send me your downloaded `schedule.ics`
"""
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)
    user_log(update, remarks="/help")


def friends(update, context):
    msg = """
I have some bot friends at SUTD, check them out!

@SUTDMapBot tells you where your think tanks are (and more)!

@evs_notification_bot tells you about your air-con credits!

@shimekiribot keeps an eye on your due days.
"""
    update.message.reply_text(msg)
    user_log(update, remarks="/friends")


def source(update, context):
    msg = "View source / contribute / report issue on [GitHub](https://github.com/MarkHershey/calendar-generator)"
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)
    user_log(update, remarks="/source")


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    user_log(update, remarks="echo")


def ics(update, context):
    # get file type
    file_type = update.message.document.mime_type
    # proceed only if the file is an ics
    if file_type == "text/calendar":
        # update.message.reply_text("Received!", parse_mode=telegram.ParseMode.MARKDOWN)
        logger.debug("New file (text/calendar) received.")
        ts: str = timestamp_now()
        file_id = update.message.document.file_id
        tg_file_ref = context.bot.get_file(file_id)
        download_filepath: Path = usr_data_path / f"{ts}.ics"
        tg_file_ref.download(download_filepath)
        # format the ics file
        try:
            new_file, number_of_events = calendarFixer.fix(download_filepath)
            user_log(update, ts=ts, remarks="ics")
        except Exception as e:
            logger.error("re-formatting of calendar ics file has failed.")
            logger.error(str(e))
            update.message.reply_text(
                "Sorry, I failed to parse your file, please report the issue from here: /source",
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            return

        # reply back
        update.message.reply_text(
            f"{number_of_events} events successfully re-formatted!",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        context.bot.send_document(
            chat_id=update.effective_chat.id, document=open(new_file, "rb")
        )
        update.message.reply_text(
            """*Fantastic, you can now import this `xxx_new.ics` into your Google/ Apple Calendar App, but you need to do this on your computer.*

Instructions for Google Calendar:

1. Open [Google Calendar](https://calendar.google.com/) on Web.
2. At the top right, click gear-like icon and then *Settings*.
3. At the left, click *Import & Export*.
4. Click *Select file from your computer* and select the `.ics` file you get from me.
5. Choose which calendar to add the imported events to. By default, events will be imported into your primary calendar.
6. Click *Import*.
""",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )

    else:
        update.message.reply_text(
            "I can only digest `.ics` file for now.",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )


def main():
    """Start the bot"""
    config_fp = Path("src/config.conf")
    if not config_fp.is_file():
        logger.error("No Config File is Found.")
        return

    try:
        with config_fp.open() as f:
            config = json.load(f)
        bot_token: str = config["bot_token"]
        if bot_token == "REPLACE_ME":
            raise Exception()
    except Exception as e:
        logger.error("Failed getting bot token from 'config.conf'")
        return

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(bot_token, use_context=True)
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
