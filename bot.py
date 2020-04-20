#!/usr/bin/python3
# -*- coding: utf-8 -*-
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
import json
import os

def main(TOKEN: str):
    global update_id
    bot = telegram.Bot(TOKEN)
    
    if not os.path.exists('blacklist_users.txt'):
        os.mknod('blacklist_users.txt')
    if not os.path.exists('warning_text.txt'):
        os.mknod('warning_text.txt')
    if not os.path.exists('admin_ids.txt'):
        os.mknod('admin_ids.txt')
    

    
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None
    
    
    while True:
        try:
            check_messages(bot)    
        except NetworkError:
            sleep(1)
        except Unauthorized:
            update_id += 1
        except (KeyboardInterrupt, SystemExit):
            print()
            print("Bye")
            print()
            exit(0)

def check_messages(bot):
    global update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1
        print(update_id, end="\r")

        if update.message:
            print(update.message)
            validate_message(bot, update.message)
            print()
def validate_message(bot, message):
    blacklist_users = open("blacklist_users.txt").read().split("\n")
    warning_text = open("warning_text.txt").read().split("\n")
    admin_ids = open("admin_ids.txt").read().split("\n")
    
    if message.new_chat_members:
        if (message.new_chat_members[0]["username"] in blacklist_users) or (message.new_chat_members[0]["id"] in blacklist_users):
            message.chat.kick_member(
                message.new_chat_members[0]["id"]
                )
            bot.send_message(
                chat_id=message.chat.id,
                text="{username} has been banned ! 😠 \nReason : Blacklist".format(
                    username=message.new_chat_members[0].name
                    )
                )
            print("Banned @{username} : Blacklist".format(
                username=message.new_chat_members[0]["username"]
                ))
    if message["text"]:
        print("Text message : " + message.text)
        for part in warning_text:
            if part in message["text"].lower():
                message.reply_text(
                    text="⚠️ WARNING ⚠️\n {username} have sent a suspicious message ...".format(
                        username=message.from_user.name
                        )
                    )
                for admin in admin_ids:
                    if admin:
                        print("Admin id : " + admin)
                        bot.send_message(admin, "⚠️ WARNING ⚠️\n {username} have sent a suspicious message ...".format(
                            username=message.from_user.name
                            ))
                        bot.forward_message(admin, message.chat.id, message.message_id, disable_notification=True)
                break
        if message.text == "/moderator" or message.text == "/moderator@bullhead_bot":
            if message.reply_to_message:
                open("admin_ids.txt", 'a').write("\n" + str(message.reply_to_message.from_user.id))
                message.reply_text("Added to moderator list. \n{user} please click [here](t.me/bullhead_bot) and start to allow the bot to notify you. ".format(user=message.reply_to_message.from_user.name))
            else:
                open("admin_ids.txt", 'a').write("\n" + str(message.from_user.id))
                message.reply_text("Added to moderator list. \n{user} please click [here](t.me/bullhead_bot) and start to allow the bot to notify you. ".format(user=message.from_user.name))
        if message.text.startswith("/ban"):
            if message.reply_to_message:
                message.chat.kick_member(
                    message.new_chat_members[0]["id"]
                )
                bot.send_message(
                    chat_id=message.chat.id,
                    text="{username} has been banned ! 😠 \nReason : Blacklist".format(
                        username=message.new_chat_members[0].name
                    ))
            print("Banned @{username} : Blacklist".format(
                username=message.new_chat_members[0]["username"]
                ))

                

    


if __name__ == '__main__':
    TOKEN = open('TOKEN').read()
    main(TOKEN)
    

