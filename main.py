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
from telegram.ext.dispatcher import run_async

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
            username = query.message.text[:query.message.text.index('\n')]
            print(username)
        except AttributeError:
            query = None
            username = f'@{update.message.from_user.username}\n'
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
                                           text = username + '\n' + f'REROLLED {message_text}\n' + text ,
                                           reply_markup = reply_markup ,
                                           parse_mode = ParseMode.HTML
                                           )
        else:
            update.message.bot.send_message(chat_id = update.message.chat_id ,
                                            text=username + '\n' + text,
                                            reply_markup = reply_markup ,
                                            parse_mode = ParseMode.HTML
                                            )
    except (LengthException ,CountException, DiceException):
         pass

@run_async
def roll_stats(update, context):
    '''Roll stats by template dnd 5e.
    Roll 6 4d6 and 3 most regular 6 times

    Command use to call:
    /rs
    /rstats
    '''
    roll: Dice
    text = str()
    all_roll = []
    username = f'@{update.message.from_user.username}'
    # Roll stats
    for x in range(6):
        roll = Dice()
        roll.rollStats()
        min_roll = min(roll.result)
        # min roll result
        roll_result_text = re.sub(f'{min_roll}' , f'<b>{min_roll}</b>' , str(roll.result) , count=1)
        # formating text
        all_roll.append(f'<b>{roll.result_stats}</b> : {roll_result_text}\n')
    # Sort by min or max
    if len(context.args) != 0:
        if context.args[0] == '+':
            # from more to less
            all_roll.sort(key=lambda x: int(
                re.search(r'^<b>\d+', x).group(0)[3:])
                )
            all_roll.reverse()
        elif context.args[0] == '-':
            # from less to more
            all_roll.sort(key=lambda x: int(
                re.search(r'^<b>\d+', x).group(0)[3:])
                )
    # Message
    # add every roll to message
    for x in all_roll:
        text += x
    # send message to user
    update.message.bot.send_message(chat_id = update.message.chat_id,
                                    text = username + '\n' + text,
                                    parse_mode=ParseMode.HTML
                                    )

@run_async
def roll_fate_dice(update , context):
    roll = Dice()
    try:
        roll.rollFateDice(mod = int(context.args[0]))
    except IndexError:
        roll.rollFateDice()
    rf = re.sub(r'[\',\,]' , '' , str(roll.result_fate)[1:-1])
    text = f'@{update.message.from_user.username}\n'
    text += f'{rf} = <b>{roll.result_int}</b>'
    update.message.bot.send_message(chat_id = update.message.chat_id,
                                    text = text,
                                    parse_mode = ParseMode.HTML
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
    dp.add_handler(CallbackQueryHandler(roll))
    dp.add_handler(CommandHandler(['rstats' , 'rs'], roll_stats))
    dp.add_handler(CommandHandler('rf' , roll_fate_dice))
    dp.add_handler(CommandHandler('start', start))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
