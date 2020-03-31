#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""All server work with telegram-bot"""

import logging
import re

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

import config

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    pass

@run_async
def roll(update , context):
    try:
        if update.callback_query != None:
            query = update.callback_query
            idm = query.message.chat_id
            username = re.search(r'(?<=@)\w+', query.message.text).group(0)
            message_text = re.search(
                r'(?<=rolled:).+(?<=(\d|F))', query.message.text).group(0)
            send_message = query.message.bot.send_message
            query.edit_message_text(query.message.text)
        else: 
            idm = update.message.chat_id
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
        
        dice_operation_list = re.findall(r'(\d*d(\d+|F))+', message)
        re_message = re.sub(r'(\d*d(\d+|F))+', '%s', message)

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
                        InlineKeyboardButton('Reroll'),
                        ]])

        send_message(chat_id=idm,
                     text=text,
                     reply_markup = reply_markup,
                     parse_mode = ParseMode.HTML
                    )

    except LengthException:
        text = """ERROR"""
        send_message(chat_id = idm,
                     text=text,
                     parse_mode = ParseMode.HTML
                    )
    except CountException:
        text = """ERROR"""
        send_message(chat_id=idm,
                     text=text,
                     parse_mode=ParseMode.HTML
                     )
    except DiceException:
        text = """ERROR"""
        send_message(chat_id=idm,
                     text=text,
                     parse_mode=ParseMode.HTML
                     )

def roll_stats():
    pass

def roll_fate_dice():
    pass 

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Run bot"""
    # Create Updater and pass it's your bot token
    updater = Updater(config.TOKEN, request_kwargs = config.REQUEST_KWARGS , use_context=True)

    # Get the dispatcher to register Handlers
    dp = updater.dispatcher

    # on different command - answer on Telegram
    dp.add_handler(MessageHandler(Filters.text, roll))
    dp.add_handler(CallbackQueryHandler(roll))
    # dp.add_handler(CommandHandler(['rstats' , 'rs'], roll_stats))
    # dp.add_handler(CommandHandler('rf' , roll_fate_dice))
    dp.add_handler(CommandHandler('start', start))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
