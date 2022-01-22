#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""All server work with telegram-bot"""

import logging
import re
import os
import sys
import configparser

from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import ParseMode
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.ext import CallbackQueryHandler
from telegram.ext import InlineQueryHandler
from telegram.ext.dispatcher import run_async

from dice_roll import *
from exceptions import LengthException
from exceptions import CountException
from exceptions import DiceException

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
config = configparser.ConfigParser()
config.read(os.getenv("CONFIG"))

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        logger.info(mode)
        updater.start_polling()
elif mode == "prod":
    rk = None
    def run(updater):
        logger.info(mode)
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook(
            f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def start(update, context):
    logger.info(f"User {update.message.from_user.id} start/restart using bot!")
    text = config["messages.start"]["text"]
    update.message.bot.send_message(
        chat_id = update.message.chat_id,
        text=text,
        parse_mode=ParseMode.HTML
        )


def roll_genericdice(update, context):
    message = re.sub(r'\s+', ' ', update.message.text).strip()
    dice_operation = re.findall(r'((\d*)d(\d+))+', message)
    message_template = re.sub(r'(\d*d\d+)+', '%s', message)
    # rolling
    dices = []
    for _, count, dim in dice_operation:
        count = int(count) if count != "" else 1
        dim = int(dim)
        dices.append((count, dim))
    result = GenericDice.roll_list(dices)
    # send back
    numeric_result = [res.numeric for res in result]
    message_template %= tuple(map(str, numeric_result))
    if len(result) > 1:
        return_message = "%d : %s" % (sum(numeric_result), message_template)
    else:
        return_message = sum(numeric_result)
    update.message.bot.send_message(
        chat_id = update.message.chat_id,
        text=return_message,
        parse_mode=ParseMode.HTML
        )


# @run_async
# def roll_handler(update, context):
#     # for rerolls 
#     if update.callback_query != None:
#         query = update.callback_query
#         # In head of last message search username
#         username = re.search(r'(?<=@)\w+', query.message.text).group(0)
#         # In last message search message_roll
#         message_text = re.search(
#             r'(?<=rolled).+(?<=:)', query.message.text).group(0)[:-1]
#         query.edit_message_text(query.message.text_html, parse_mode=ParseMode.HTML)
#         roll(
#             idm = query.message.chat_id,
#             user_id = query.message.from_user.id,
#             username = username,
#             message_text = message_text,
#             send_message = query.message.bot.send_message,
#         )


#     # for simple roll
#     else:
#         roll(
#             idm = update.message.chat_id,
#             user_id = update.message.from_user.id,
#             username = update.message.from_user.username,
#             message_text = update.message.text,
#             send_message = update.message.bot.send_message,
#         )


# def roll(inline_mode: bool = False, **kwargs):
#     # Start set
#     num_of_str = 3
#     template_group = "@{username} rolled <b>{message}</b>:\n" + num_of_str*"{}"
#     template_private = "<b>{message}</b>:" + num_of_str*"{}"
#     idm, user_id, username, message_text, send_message = kwargs.values()

#     try:
#         # remove whitespase
#         message = re.sub(r'\s{2,}', ' ', message_text)

#         # Exception
#         if len(message) > 300:
#             raise LengthException
#         elif re.search(r'\d\d\d\dd', message) != None:
#             raise CountException
#         elif re.search(r'd\d\d\d\d', message):
#             raise DiceException
        
#         dice_operation_list = re.findall(r'(\d*d(\d+|F)[A,a,D,d]?)+', message)
#         re_message = re.sub(r'(\d*d(\d+|F)[A,a,D,d]?)+', '%s', message)

#         roll_list = Dice.rollList(dice_operation_list, crit_highlight=True)

#         # Lists of results rolling for formating 
#         result_num = re_message % tuple([str(int(x)) for x in roll_list])
#         result_rude = re_message % tuple([Dice.Cut(x) for x in roll_list])

#         result_num_to_text = (re.search(r'[\+,\-,\*]', re_message) != None)
#         result_rude_to_text = any([x.count > 1 for x in roll_list])

#         # formating text
#         return_message = template_private.format(
#                         ' '*4 + f'<code>{result_rude}</code>\n' \
#                                 if result_rude_to_text else str(), 
#                         ' '*4 + f'{result_num}\n' \
#                             if result_num_to_text else str(), 
#                         f'Total: <b>{round(eval(result_num))}</b>',
#                         username=username,
#                         message=message,
#                         )

#         reply_markup = InlineKeyboardMarkup([[
#                         InlineKeyboardButton('Reroll', callback_data='reroll'),
#                         ]])

#         # Work with logs
#         logger.info(f"User {user_id} roll: {str(result_num)}={str(result_rude)} original m: {message}")

#         send_message(chat_id=idm,
#                      text=return_message,
#                      reply_markup=reply_markup,
#                      parse_mode=ParseMode.HTML
#                     )

#     except LengthException:
#         pass


# def roll_stats(update, context, inline_mode=False):
#     '''Roll stats for dnd5'''
#     vrolls = 6
#     sort_type = None
#     sort_type_bymax = ('max', 'bymax', 'h',)
#     sort_type_bymin = ('min', 'bymin', 'l',)
#     try:
#         idm = update.message.chat_id
#         message = re.split(r'\s', update.message.text)
#         if message != ['/rs']:
#             message = message[1:]
#             for i in message:
#                 if i in sort_type_bymax + sort_type_bymin:
#                     sort_type = i
#                 else:
#                     vrolls = int(i)
                    

#         stats = [Dice().rollStats() for x in range(vrolls)]
#         if sort_type in (sort_type_bymax + sort_type_bymin):
#             rev = sort_type in sort_type_bymax
#             stats.sort(key=lambda x: x.result_sum , reverse=rev)
#         text = f"@{update.message.from_user.username}\n"+\
#                '%s\n'*vrolls % tuple([f'{str(x)} : {str(x.result_sum)}' for x in stats])

#         logging.info(f"{update.message.from_user.id} roll stats {text}")

#         update.message.bot.send_message(chat_id=idm,
#                                         text=text,
#                                         parse_mode=ParseMode.HTML
#                                         )
#     except LengthException:
#         pass


# def roll_fate_dice(update , context, inline_mode=False):
#     setting = ('adv','a','d','disadv')
#     template = '{visual}{bonus} = {total}'
#     try:
#         # type message check
#         idm = update.message.chat_id
#         message = re.split(r'\s', update.message.text)
#         is_group = update.message.chat.type == 'group'

#         # get setting roll by user       
#         if message != ['/rf']:
#             # exclude '/rf'
#             message = message[1:]
#             with_bonus = False
#             with_adv = False
#             for i in message:
#                 if i in setting:
#                     arg = i
#                     with_adv = True
#                 else:
#                     bonus = int(i)
#                     with_bonus = True

#                 if not with_adv:
#                     arg = None
#                 if not with_bonus:
#                     bonus = 0
#         else:
#             arg = None
#             bonus = 0

#         roll = Dice(adv = arg).rollFateDice(4)

#         # formating
#         if bonus < 0:
#             bonus_text = str(bonus)
#         elif bonus == 0:
#             bonus_text=''
#         else:
#             bonus_text = f'+{bonus}'

#         if is_group:
#             template = f'@{update.message.from_user.username}\n'+template

#         text = template.format(
#             bonus=bonus_text,
#             visual=str(roll),
#             total=int(roll)+bonus,
#         )

#         logging.info(f"{update.message.from_user.id} roll fuadje dice {text}")

#         update.message.bot.send_message(chat_id=idm,
#                                         text=text,
#                                         parse_mode=ParseMode.HTML
#                                         )
#     except LengthException:
#         pass


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    """Run bot"""
    logger.info("Starting bot")
    # Create Updater and pass it's your bot token
    updater = Updater(
        TOKEN, use_context=True
        )

    # Get the dispatcher to register Handlers
    dp = updater.dispatcher

    # Commands handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, roll_genericdice, run_async=True))
    # dp.add_handler(CommandHandler(['rstats', 'rs'], roll_stats))
    # dp.add_handler(CommandHandler('rf', roll_fate_dice))
    # dp.add_handler(CommandHandler('start', start))
    # # Other handlers
    # dp.add_handler(MessageHandler(Filters.text, roll_handler))
    # dp.add_handler(CallbackQueryHandler(roll_handler))
    # dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    run(updater)
