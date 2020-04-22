#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os
import re
from time import sleep
import traceback

import telegram
from telegram.error import NetworkError, Unauthorized


def main(TOKEN: str):
    global update_id, authorized_chats, admin_ids
    bot = telegram.Bot(TOKEN)
    
    if not os.path.exists('blacklist_users.txt'):
        os.mknod('blacklist_users.txt')
    if not os.path.exists('warning_text.txt'):
        os.mknod('warning_text.txt')
    if not os.path.exists('admin_ids.txt'):
        os.mknod('admin_ids.txt')
    if not os.path.exists('authorized_chats.txt'):
        os.mknod('authorized_chats.txt')
    authorized_chats = open("authorized_chats.txt").read().split("\n")
    admin_ids = open("admin_ids.txt").read().split("\n")

    
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
        except:
            traceback.print_exc()



def check_messages(bot):
    global update_id, authorized_chats, admin_ids
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            if (str(update.message.chat.id)  in authorized_chats) and (update.message.chat.type == "group"):
                validate_message(bot, update.message)
            elif (str(update.message.chat.id)  in authorized_chats) and (update.message.chat.type == "supergroup"):
                validate_message(bot, update.message)
            elif (str(update.message.chat.id)  in admin_ids) and (update.message.chat.type == "private"):
                validate_message(bot, update.message)
            else:
                print("Unauthorized access !!! : \n{}\n\n".format(update.message))
                bot.send_message(
                    chat_id=update.message.chat.id,
                    text="Chat not in list, remove this bot from your chat."
                    )
def validate_message(bot, message):
    global admin_ids
    blacklist_users = [x for x in open("blacklist_users.txt").read().split("\n") if x]
    warning_text = [x for x in open("warning_text.txt").read().split("\n") if x]
    admin_ids = [ x for x in open("admin_ids.txt").read().split("\n") if x]
    if message.chat.type == "private":
        chat_admins = []
    else:
        chat_admins = bot.get_chat_administrators(message.chat.id)
    chat_admins = [x.user.id for x in chat_admins]
    if message.new_chat_members:
        if (message.new_chat_members[0]["username"] in blacklist_users) or (str(message.new_chat_members[0]["id"]) in blacklist_users): # Blacklist
            message.chat.kick_member(
                int(message.new_chat_members[0]["id"])
                )
            bot.send_message(
                chat_id=message.chat.id,
                text="{username} has been banned ! 😠 \nReason : Blacklisted".format(
                    username=message.new_chat_members[0].name
                    )
                )
            print("Banned @{username} : Blacklisted".format(
                username=message.new_chat_members[0]["username"]
                ))
            return
        for part in warning_text: #Username ban
            if part in message.new_chat_members[0]["username"]:
                message.chat.kick_member(
                    message.new_chat_members[0]["id"]
                    )
                bot.send_message(
                    chat_id=message.chat.id,
                    text="{username} has been banned ! 😠 \nReason : Weird username".format(
                        username=message.new_chat_members[0].name
                        )
                    )
                print("Banned @{username} : Weird username".format(
                    username=message.new_chat_members[0]["username"]
                    ))
            return
    elif message["text"]:
        needBan = False
        for part in warning_text:
            if part in message["text"].lower():
                needBan=True
        if needBan:
            custom_keyboard = [["Ban {} (Username : {}) from {}.".format(str(message.from_user.id), message.from_user.name, str(message.chat.id)), "Don't ban  {}".format( message.from_user.name)  ]]
            reply_markup = telegram.ReplyKeyboardMarkup(
                custom_keyboard, one_time_keyboard=True, selective=True)
            message.reply_text(
                text="⚠️ WARNING ⚠️\n {username} has sent a suspicious message ...".format(
                    username=message.from_user.name,
                    )
                )
            for admin in admin_ids:
                if admin:
                    print("Admin id : " + admin)
                    bot.send_message(admin, "⚠️ WARNING ⚠️\n {username} has sent a suspicious message ...".format(
                        username=message.from_user.name,
                        ),
                        reply_markup=reply_markup)
                    bot.forward_message(admin, message.chat.id, message.message_id, disable_notification=True, reply_markup=reply_markup)

        if str(message.from_user.id) in admin_ids:
            if (message.text == "/moderator" or message.text == "/moderator@bullhead_bot") and (message.from_user.id in chat_admins):
                if str(message.reply_to_message.from_user.id) in admin_ids:
                    message.reply_text(message.reply_to_message.from_user.name + " is already a moderator. ", disable_notification=True)
                    return

                if message.reply_to_message:
                    open("admin_ids.txt", 'a').write("\n" + str(message.reply_to_message.from_user.id))
                    message.reply_text("Added to moderator list. \n{user} please folow this link {link} and start to allow the bot to notify you. ".format(user=message.reply_to_message.from_user.name, link=bot.link))
                else:
                    open("admin_ids.txt", 'a').write("\n" + str(message.from_user.id))
                    message.reply_text("Added to moderator list. \n{user} please click [here](t.me/bullhead_bot) and start to allow the bot to notify you. ".format(user=message.from_user.name))

            elif message.text.startswith("/ban"):
                if message.reply_to_message:
                    message.chat.kick_member(
                        message.reply_to_message.from_user.id
                    )
                    open("blacklist_users.txt", "a").write(str(message.reply_to_message.from_user.id) + "\n")
                    if message.text[4:].startswith("@bullhead_bot"): message.text = "/ban " + message.text[18:]
                    bot.send_message(
                        chat_id=message.chat.id,
                        text="{username} has been banned ! 😠 \nReason : {reason}".format(
                            username=message.reply_to_message.from_user.name,
                            reason=message.text[4:]
                        ))
                    print("Banned {username} : Manual ban ({reason})".format(
                        username=message.reply_to_message.from_user.name,
                        reason=message.text[4:]
                        ))

            elif message.text.startswith("/unmoderator") and (message.from_user.id in chat_admins):
                if message.reply_to_message:
                    for i, line in enumerate(admin_ids):
                        if str(message.reply_to_message.from_user.id) == line:
                            del admin_ids[i]
                            os.remove("admin_ids.txt")
                            with open("admin_ids.txt", 'a') as f:
                                for admin in admin_ids:
                                    f.write(admin + "\n")
                            bot.send_message(message.chat.id, "Done. ")
                            return
            elif message.text.startswith("Ban "):
                regex = re.search(r"Ban (.+?) \(Username : (.+?)\) from (.+?)\.", message.text)
                banId = regex.group(1)
                groupId = regex.group(3)
                username = regex.group(2)
                bot.kick_chat_member(chat_id=int(groupId), user_id=int(banId))
                open("blacklist_users.txt", "a").write(str(banId) + "\n")
                bot.send_message(
                    chat_id=groupId,
                    text="{username} has been banned ! 😠 \nReason : Spammer".format(
                        username=username,
                    ))
                print("Banned {username} : Manual ban (Spammer)".format(
                    username=username,
                    ))

        elif message.text in ["/moderator", "/moderator@bullhead_bot", "/ban", "/ban@bullhead_bot", "/unmoderator"]:
            bot.send_message(
                chat_id=message.chat.id,
                text="Why does non-moderator tell me what to do ?"
                )




if __name__ == '__main__':
    TOKEN = open('TOKEN').read()
    main(TOKEN)
