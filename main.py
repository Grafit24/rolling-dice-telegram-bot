#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""All server work with telegram-bot"""

import logging
import re

from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.ext import CallbackQueryHandler
from telegram import CallbackQuery
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import ParseMode

from dice_roll import Dice
from message import separateMessage
from exceptions import LengthException
from exceptions import CountException
from exceptions import DiceException

import config

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    pass


def roll(update, context):
    """Roll dices by message and calculate more these"""
    roll: Dice
    query: CallbackQuery
    message_text: str
    message: list
    text: str
    count_str: str
    all_roll: list
    count: int
    reply_markup: InlineKeyboardMarkup
    try:
        try:
            query = update.callback_query
            message_text = query.data
        except AttributeError:
            query = None
            message_text = update.message.text
        #
        if len(message_text) > 300:
            raise LengthException(len(message_text))
        # Get separate message by operators
        message = separateMessage(message_text)
        print(message)

        # Roll operation
        text = str()
        count_str = str()
        all_roll = list()
        for x in message:
            if 'd' in x:
                # Roll expressions
                roll = Dice()
                roll.Roll(x)
                all_roll.append(roll)
                # add result roll to the answer
                text += str(tuple(roll.result))
                # add result roll to the eval var
                count_str += str(sum(roll.result))
            else:
                # add simple number and operators
                text += x
                count_str += x
        # count of expressins
        count = eval(count_str)

        # Formatting text
        if roll.count > 1:
            text += ' =\n'
        else:
            text = ''
        if len(message) > 1:
            text += f'= {count_str} =\n'
        text += '<b>' + str(round(count)) + '</b>'

        # Check crit
        if roll.dice == 20 and sum(roll.result) == 20 and roll.count == 1:
            text += ' : Critical Hit!'
        elif roll.dice == 20 and sum(roll.result) == 1 and roll.count == 1:
            text += ' : Critical Fail!'

        # Set last message
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton('Reroll', callback_data=message_text)
        ]])
        if query != None:
            query.edit_message_text(query.message.text)
            query.message.bot.send_message(chat_id = query.message.chat_id ,
                                           text = f'REROLLED {message_text}\n' + text ,
                                           reply_markup = reply_markup ,
                                           parse_mode = ParseMode.HTML
                                           )
        else:
            update.message.bot.send_message(chat_id = update.message.chat_id ,
                                            text = text ,
                                            reply_markup = reply_markup ,
                                            parse_mode = ParseMode.HTML
                                            )
    except (LengthException ,CountException, DiceException):
         pass


def roll_stats(update, context):
    text: str
    roll: Dice
    text = ''
    username = f'@{update.message.from_user.username}'
    for x in range(6):
        roll = Dice()
        roll.rollStats()
        min_roll = min(roll.result)
        # min roll result
        roll_result_text = re.sub(f'{min_roll}' , f'<b>{min_roll}</b>' , str(roll.result) , count=1)
        text += f'<b>{roll.result_stats}</b> : {roll_result_text}\n'
    update.message.bot.send_message(chat_id = update.message.chat_id,
                                    text = username + '\n' + text,
                                    parse_mode=ParseMode.HTML
                                    )


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
    dp.add_handler(CommandHandler('r', roll))
    dp.add_handler(CallbackQueryHandler(roll))
    dp.add_handler(CommandHandler('rstats', roll_stats))
    dp.add_handler(CommandHandler('start', start))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
