#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""All server work with telegram-bot"""

import logging
import re
import os
import sys

from telegram import CallbackQuery
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import ParseMode
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.ext import CallbackQueryHandler
from telegram.ext.dispatcher import run_async

from dice_roll import Dice
from exceptions import LengthException
from exceptions import CountException
from exceptions import DiceException
from telegram.error import BadRequest

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    PROXY = os.getenv("PROXY")
    logger.info(str(PROXY))
    rk = {
        'proxy_url': f'socks5://{PROXY}',
    }
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
            "https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN)
            )
else:
    logger.error("No MODE specified!")
    sys.exit(1)



def start(update, context):
    logger.info(f"User {update.message.from_user.id} start use bot")
    text = """Bot is in develop. U can use it.
    NdNa + ...(float blocked)
        a can be (adv - A , disadv - D)
        N - is natural number
    /rs
        Roll stats by template dnd5
    /rf 
        Roll fudge dice
    """
    update.message.bot.send_message(chat_id = update.message.chat_id,
                            text=text,
                            parse_mode=ParseMode.HTML
                            )

@run_async
def roll(update , context):
    try:
        if update.callback_query != None:
            query = update.callback_query
            idm = query.message.chat_id
            user_id = query.message.from_user.id
            username = re.search(r'(?<=@)\w+', query.message.text).group(0)
            message_text = re.search(
                r'(?<=rolled:).+(?<=((\d|F))|([A,a,D,d]))', query.message.text).group(0)
            send_message = query.message.bot.send_message
            query.edit_message_text(query.message.text)
        else: 
            idm = update.message.chat_id
            user_id = update.message.from_user.id
            username = update.message.from_user.username
            message_text = update.message.text
            send_message = update.message.bot.send_message

        message = re.sub(r'( ){2,}', ' ', message_text)

        if len(message) > 300:
            raise LengthException
        elif re.search(r'\d\d\d\dd', message) != None:
            raise CountException
        elif re.search(r'd\d\d\d\d', message):
            raise DiceException
        
        dice_operation_list = re.findall(r'(\d*d(\d+|F)[A,a,D,d]?)+', message)
        re_message = re.sub(r'(\d*d(\d+|F)[A,a,D,d]?)+', '%s', message)

        roll_list = Dice.rollList(dice_operation_list)

        # Lists of results rolling for formating 
        result_int = re_message % tuple([str(int(x)) for x in roll_list])
        result_str = re_message % tuple([Dice.Cut(x) for x in roll_list])

        result_int_to_text = (re.search(r'[\+,\-,\*]', re_message) != None)
        result_str_to_text = any([x.count > 1 for x in roll_list])

        template = f'@{username} rolled: {message}\nRESULT:\n%s%s%s'
        text = template % (4*' ' + f'{result_str}\n' if result_str_to_text else str() , 
                           4*' ' + f'{result_int}\n' if result_int_to_text else str(), 
                           f'<b>{round(eval(result_int))}</b>'
                           )

        reply_markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton('Reroll', callback_data='template'),
                        ]])

        # Work with logs
        logger.info(f"User {user_id} roll: {str(result_str)}={str(result_int)}")

        send_message(chat_id=idm,
                     text=text,
                     reply_markup = reply_markup,
                     parse_mode = ParseMode.HTML
                    )

    except LengthException:
        logger.info(f"Length exception {user_id}")
        text = """ERROR"""
        send_message(chat_id = idm,
                     text=text,
                     parse_mode = ParseMode.HTML
                    )
    except CountException:
        logger.info(f"Count exception {user_id}")
        text = """ERROR"""
        send_message(chat_id=idm,
                     text=text,
                     parse_mode=ParseMode.HTML
                     )
    except DiceException:
        logger.info(f"Dice exception {user_id}")
        text = """ERROR"""
        send_message(chat_id=idm,
                     text=text,
                     parse_mode=ParseMode.HTML
                     )

def roll_stats(update , context):
    '''Roll stats for dnd5'''
    vrolls = 6
    sort_type = None
    sort_type_bymax = ('max', 'bymax', 'h',)
    sort_type_bymin = ('min', 'bymin', 'l',)
    try:
        idm = update.message.chat_id
        if context.args != list():
            sort_type, vrolls = context.args 
            vrolls = int(vrolls)

        stats = [Dice().rollStats() for x in range(vrolls)]
        if sort_type in (sort_type_bymax + sort_type_bymin):
            rev = sort_type in sort_type_bymax
            stats.sort(key=lambda x: x.result_sum , reverse=rev)
        text = f"@{update.message.from_user.username}\n"+\
               '%s\n'*vrolls % tuple([f'{str(x)} : {str(x.result_sum)}' for x in stats])

        logging.info(f"{update.message.from_user.id} roll stats {text}")

        update.message.bot.send_message(chat_id=idm,
                                        text=text,
                                        parse_mode=ParseMode.HTML
                                        )
    except LengthException:
        pass

def roll_fate_dice(update , context):
    setting = ('adv','a')
    try:
        idm = update.message.chat_id
        if context.args != list():
            arg = True if (context.args[0] in setting[1]) else False 
        else:
            arg = None
        roll = Dice(adv = arg).rollFateDice(4)
        text = f'{str(roll)} = {int(roll)}'

        logging.info(f"{update.message.from_user.id} roll fuadje dice {text}")

        update.message.bot.send_message(chat_id=idm,
                                        text=text,
                                        parse_mode=ParseMode.HTML
                                        )
    except LengthException:
        pass

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    """Run bot"""
    logger.info("Starting bot")
    # Create Updater and pass it's your bot token
    updater = Updater(
        TOKEN, request_kwargs=rk, use_context=True
        )

    # Get the dispatcher to register Handlers
    dp = updater.dispatcher

    # on different command - answer on Telegram
    dp.add_handler(MessageHandler(Filters.text, roll))
    dp.add_handler(CallbackQueryHandler(roll))
    dp.add_handler(CommandHandler(['rstats', 'rs'], roll_stats))
    dp.add_handler(CommandHandler('rf', roll_fate_dice))
    dp.add_handler(CommandHandler('start', start))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    run(updater)
