import json
import os
from pathlib import Path
from typing import Any

# external modules
import telegram
from puts import get_logger, timestamp_microseconds
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)
from telegram.utils.helpers import escape_markdown

# internal modules
import calendarFixer

LOGGER = get_logger(reset=True)

curr_folder: Path = Path(__file__).parent.resolve()
project_root: Path = curr_folder.parent
usr_data_path: Path = project_root / "usr_data"
logs_path: Path = project_root / "logs"
user_log_fp: Path = logs_path / "user_visit_history.txt"

logs_path.mkdir(parents=True, exist_ok=True)
usr_data_path.mkdir(parents=True, exist_ok=True)

unique_users = set()
interaction_counter: int = 0
parse_mode: str = telegram.ParseMode.MARKDOWN

###############################################################################
# Helper Functions


def escape_md(string: Any) -> str:
    return escape_markdown(str(string), version=2)


def load_stats() -> None:
    global interaction_counter
    global unique_users

    if user_log_fp.is_file():
        with user_log_fp.open(mode="r") as f:
            data = f.readlines()
            interaction_counter = len(data)
            users = [i.split(" - ")[2][9:-1] for i in data]
            unique_users = set(users)

    print(f"{interaction_counter} interactions")
    print(f"{len(unique_users)} unique users")
    return None


def user_log(update: Update, ts: str = None, remarks: str = "") -> None:
    global interaction_counter
    global unique_users

    if not ts:
        ts: str = timestamp_microseconds()
    first_name: str = update.message.from_user.first_name
    last_name: str = update.message.from_user.last_name
    username: str = update.message.from_user.username
    _id: str = update.message.from_user.id

    name: str = f"{first_name} {last_name}"
    unique_users.add(username)
    interaction_counter += 1
    record: str = (
        f"{ts} - id({_id}) - username({username}) - name({name}) - visited({remarks})\n"
    )
    with user_log_fp.open(mode="a") as f:
        f.write(record)
    return None


def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    LOGGER.error(f'Update "{update}" caused error "{context.error}"')
    return None


def start(update: Update, context: CallbackContext) -> None:
    msg = f"""
Howdy {update.message.from_user.first_name},

Send me your `schedule.ics`, I will make it look *prettier*!

First time here? Use /help

/help : check how to download your schedule.

/friends : get to know my friends.

/source : view source or report issues.
"""
    update.message.reply_text(msg, parse_mode=parse_mode)
    user_log(update, remarks="/start")
    return None


def stats(update: Update, context: CallbackContext) -> None:
    global interaction_counter
    global unique_users

    msg = f"To date, I have served {len(unique_users)} unique users in {interaction_counter} interactions."
    update.message.reply_text(msg)
    user_log(update, remarks="/stats")
    return None


def _help(update: Update, context: CallbackContext) -> None:
    msg = """
Do you know that you can import your class schedule into your Google Calendar?

You can download an importable `.ics` file from SUTD, but the original file is badly formatted and it won't look good on your calendar App.

This bot helps you clean up the mess in the `.ics` file so that you will get a neat calendar view.

Follow the step-by-step instructions to download your schedule, then *come back and send the file you downloaded to me (this chat)*.

1.  Visit [https://mymobile.sutd.edu.sg/app/dashboard](https://mymobile.sutd.edu.sg/app/dashboard)
2.  Use your SUTD Network ID (`100xxxx`) to log in
3.  From left-hand side menu -> Choose *Schedule*
4.  Top-right gear-like button -> Choose *Download Schedule*

Send me your downloaded `schedule.ics`
"""
    update.message.reply_text(msg, parse_mode=parse_mode)
    user_log(update, remarks="/help")
    return None


def friends(update: Update, context: CallbackContext) -> None:
    msg = """
I have some bot friends at SUTD, check them out!

@SUTDMapBot tells you where your think tanks are (and more)!

@evs_notification_bot tells you about your air-con credits!

@shimekiribot keeps an eye on your due days.
"""
    update.message.reply_text(msg)
    user_log(update, remarks="/friends")
    return None


def source(update: Update, context: CallbackContext) -> None:
    msg = "View source code / contribute / report issues on [GitHub](https://github.com/MarkHershey/sutd-calendar-fixer)"
    update.message.reply_text(msg, parse_mode=parse_mode)
    user_log(update, remarks="/source")
    return None


def echo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    user_log(update, remarks="echo")
    return None


def ics(update: Update, context: CallbackContext) -> None:
    # get file type
    file_type = update.message.document.mime_type
    # proceed only if the file is an ics
    if file_type == "text/calendar":
        # update.message.reply_text("Received!", parse_mode=parse_mode)
        LOGGER.info("New file (text/calendar) received.")
        ts: str = timestamp_microseconds()
        file_id = update.message.document.file_id
        tg_file_ref = context.bot.get_file(file_id)
        download_filepath: Path = usr_data_path / f"{ts}.ics"
        tg_file_ref.download(download_filepath)
        # format the ics file
        try:
            new_filepath, number_of_events = calendarFixer.fix(download_filepath)
            user_log(update, ts=ts, remarks="ics")
        except Exception as e:
            LOGGER.error("re-formatting of calendar ics file has failed.")
            LOGGER.error(str(e))
            msg = "Sorry, I failed to parse your file, please report the issue from here: /source"
            update.message.reply_text(msg, parse_mode=parse_mode)
            return

        # reply back
        msg = f"{number_of_events} events successfully re-formatted!"
        update.message.reply_text(msg, parse_mode=parse_mode)
        document = open(new_filepath, "rb")
        context.bot.send_document(chat_id=update.effective_chat.id, document=document)
        msg = """*Fantastic, you can now import this `xxx_new.ics` into your Google/ Apple Calendar App, but you need to do this on your computer.*

Instructions for Google Calendar:

1. Open [Google Calendar](https://calendar.google.com/) on Web.
2. At the top right, click gear-like icon and then *Settings*.
3. At the left, click *Import & Export*.
4. Click *Select file from your computer* and select the `.ics` file you get from me.
5. Select the calendar to import new events into. We recommend creating a new calendar to import your SUTD timetable.
6. Click *Import*.
"""
        update.message.reply_text(msg, parse_mode=parse_mode)

    else:
        msg = "I can only digest `.ics` file for now."
        update.message.reply_text(msg, parse_mode=parse_mode)
    return None


def get_bot_token() -> str:
    """Get the bot token from the environment or the config file."""
    LOGGER.info("Getting Bot Token from environment")
    bot_token = os.environ.get("BOT_TOKEN", None)

    if bot_token == "REPLACE_ME" or bot_token is None:

        LOGGER.info("Not found in env. Getting Bot Token from src/config.conf")
        config_fp = curr_folder / "config.conf"

        if not config_fp.is_file():
            LOGGER.error("Bot Token not found: No Config File is Found.")
            raise Exception("Bot Token Not Found.")

        with config_fp.open() as f:
            config = json.load(f)
        bot_token = config.get("bot_token", None)

    if bot_token == "REPLACE_ME" or bot_token is None:
        LOGGER.error(
            "Bot Token not found: Failed getting bot token from environment and 'config.conf'"
        )
        raise Exception("Bot Token Not Found.")
    return bot_token


def main() -> None:
    """Start the bot"""
    bot_token = get_bot_token()
    load_stats()

    # Get the updater
    updater = Updater(bot_token, use_context=True)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Command Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", _help))
    dispatcher.add_handler(CommandHandler("friends", friends))
    dispatcher.add_handler(CommandHandler("source", source))
    dispatcher.add_handler(CommandHandler("stats", stats))

    # Message Handlers
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    dispatcher.add_handler(MessageHandler(Filters.document, ics))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

    return None


if __name__ == "__main__":
    main()
