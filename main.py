#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ast import parse
import logging
import os
import sys
import configparser

from telegram import InlineKeyboardMarkup, message
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
from message_parse import *
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
    text = config["messages.start"].get("text")
    update.message.bot.send_message(
        chat_id = update.message.chat_id,
        text=text,
        parse_mode=ParseMode.HTML
        )


def roll_genericdice(update, context):
    conf = config["messages.roll_genericdice"]
    template = conf.get("template")
    details = Details(crit=conf.getboolean("crit"))
    parser = GenericDiceParser(template, ":", details_parser=details)
    dices = parser.parse_input(update.message.text)
    result = GenericDice.roll_list(dices)
    return_message = parser.parse_output(
        result, verbosity=conf.getint("verbosity"))
    update.message.bot.send_message(
        chat_id = update.message.chat_id,
        text=return_message,
        parse_mode=ParseMode.HTML
        )


def roll_dnd5_generator(dice):
    def roll_dnd5(update, context):
        conf = config["messages.roll_dnd5"]
        template = conf.get("template")
        details = Details(crit=conf.getboolean("crit"))
        parser = RollsParser(template, "=", details_parser=details)
        count = parser.parse_input(update.message.text)
        result_dice = DND5Dice(count, dice)
        return_message = parser.parse_output(
            result_dice,
            verbosity=conf.getint("verbosity")
        )
        update.message.bot.send_message(
            chat_id = update.message.chat_id,
            text=return_message,
            parse_mode=ParseMode.HTML
            )
    return roll_dnd5


def roll_dnd5stats(update, cotnext):
    conf = config["messages.roll_dnd5stats"]
    template = conf.get("template_message")
    details = Details(crit=True, html_highlight=("<strike>", "</strike>"))
    parser = DND5StatsParser(
        template, conf.get("template_row"), ":", details_parser=details)
    count = parser.parse_input(update.message.text)
    result_stats = DND5Dice.roll_stats(count)
    return_message = parser.parse_output(
        result_stats,
        verbosity=conf.getint("verbosity")
        )
    update.message.bot.send_message(
        chat_id = update.message.chat_id,
        text=return_message,
        parse_mode=ParseMode.HTML
        )


def roll_fudje(update, context):
    conf = config["messages.roll_fudje"]
    template = conf.get("template")
    sep = conf.get("sep")
    details = Details(
        brackets=(conf.get("bracket_l"), conf.get("bracket_r")),
        crit=conf.getboolean("crit"),
        space=conf.get("space"),
        html_highlight=(conf.get("html_l"), conf.get("html_r"))
    )
    parser = RollsParser(template, sep, details)
    count = parser.parse_input(update.message.text)
    result_dice = FudgeDice(count)
    return_message = parser.parse_output(
        result_dice,
        verbosity=conf.getint("verbosity")
    )
    update.message.bot.send_message(
        chat_id = update.message.chat_id,
        text=return_message,
        parse_mode=ParseMode.HTML
        )


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    """Run bot"""
    logger.info("Starting bot")
    # Create Updater and pass it's your bot token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register Handlers
    dp = updater.dispatcher

    # Commands handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('dnd5stats', roll_dnd5stats))
    dp.add_handler(CommandHandler('rf', roll_fudje))
    for dice in [2, 4, 6, 8, 10, 12, 20, 100]:
        dp.add_handler(CommandHandler(f"r{dice}", roll_dnd5_generator(dice)))
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
