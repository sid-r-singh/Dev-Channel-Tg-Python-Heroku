#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

import os
import logging
from typing import Dict

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

TOKEN = os.getenv("TOKEN")
#Start change



# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ['Monte Carlo', 'Favourite colour'],
    ['Number of siblings', 'Something else...'],
    ['Done'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

reply_keyboard2 = [
    ['Yes', 'No'],
]
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True)

# Function facts_to_str to convert dict to string
def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])

# Initiate conversation
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Hi! My name is Doctor Botter"
        "Why don't you tell me something about yourself?"
        "Choose a simulation that u would like to run",
        reply_markup=markup,
    )

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')

    return TYPING_REPLY


def params_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Please enter {text.lower()}? no. of trials',reply_markup=markup2,)

    return TYPING_REPLY

def custom_choice(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Alright, please send me the category first, ' 'for example "Most impressive skill"'
    )

    return TYPING_CHOICE


def received_information(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text(
        "Neat! Just so you know, this is what you already told me:"
        f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
        " on something.",
        reply_markup=markup,
    )

    return CHOOSING

# Only way to end conversation is by pressing 'done'
# Function 'done' to do that
def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user = update.message.from_user
    if 'choice' in user_data:
        del user_data['choice']
    print(user_data)
    print(type(user_data))
    update.message.reply_text(
        f"Hey {user.first_name}, I learned these facts about you: {facts_to_str(user_data)} \nThe next time U wish to talk to me, just send\n /start to me 😊"
    )

    user_data.clear()
    return ConversationHandler.END



#End change
def run(updater):
    PORT = int(os.environ.get("PORT", "8443"))
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
    
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)





def main() -> None:
    # Create the Updater and pass it your bot's token.
    
    updater = Updater(TOKEN)
    
    #Start change
    
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    # Choosing
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Favourite colour|Number of siblings)$'), regular_choice
                ),
                MessageHandler(
                    Filters.regex('^Something else...$'), custom_choice
                ),
                MessageHandler(
                    Filters.regex('^Monte Carlo$'), params_choice
                ), 
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)
    
    #End change
    
    dispatcher.add_error_handler(error)

    run(updater)



if __name__ == '__main__':
    main()




