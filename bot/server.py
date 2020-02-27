from bot import telegram_chatbot
from telegram import File

update_id = None
bot = telegram_chatbot('config.cfg')

def make_reply(msg):
    reply = msg
    return reply


while True:
    print("...")
    updates = bot.get_updates(offset=update_id)
    updates = updates["result"]
    if updates:
        for item in updates:
            update_id = item["update_id"]

            try:
                message = item['message']['text']
            except:
                message = None

            try:
                document = item['message']['document']
            except:
                document = None

            if document != None:
                doc_name = document["file_name"]
                doc_type = document["mime_type"]
                doc_id = document["file_id"]
                doc_uid = document["file_unique_id"]
                doc_size = document['file_size']

            # actions

            # 1. reply the same message
            from_ = item['message']['from']['id']
            reply = make_reply(message)
            bot.send_message(reply, from_)

            # 2. download file if file is ics
            if document != None:
                print(doc_type)
                print(doc_name)
                if doc_type == "text/calendar" and doc_name[-4:] == ".ics":
                    # print(doc_name, doc_type, doc_id, doc_uid, doc_size, sep="\n")
                    bot.send_message(f".ics file detected \nuid: {doc_uid}", from_)
                    try:
                        ics = File(doc_id)
                        ics.download()
                    except:
                        print("Failed to download ics file to server")
