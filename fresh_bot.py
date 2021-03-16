"""
MC simulation runner
"""

import logging
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#No. of states apart from start
PAR_1, CONFIRMATION = range(2)

reply_keyboard = [['Confirm', 'Restart']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
TOKEN = os.getenv("TOKEN")
bot = telegram.Bot(token=TOKEN)
#chat_id = 'YOURTELEGRAMCHANNEL'


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


# Initiate conversation
# Changes state to PAR_1, immeaditely after sending welcome msg
def start(update, context):
    update.message.reply_text(
        "Hi! I am your High performance computing (HPC) bot. Use me to do HPC in small time.\n"
        "Currently I support only Monte Carlo program.\nSend me the no. of trials (integer expected)"
        )
    return PAR_1
   
def par_1(update, context):
	user = update.message.from_user
	user_data = context.user_data
    #Define key
	category = 'trials'
	text = update.message.text
    #Assign value
	user_data[category] = text
	logger.info("No. of trials: %s", update.message.text)
	update.message.reply_text(f"Hey {user.first_name}, you have entered the following prarameters to run MC simulation! Please confirm."
								"{}".format(facts_to_str(user_data)), reply_markup=markup)

	return CONFIRMATION

# Two ways to end conversation
# One by confirmation
# Function 'confirmation' to do that

def confirmation(update, context):
    user_data = context.user_data
    user = update.message.from_user
    update.message.reply_text(f"Thank you for confirming {user.first_name}. I will soon update you with result.", reply_markup=ReplyKeyboardRemove())
    print(user_data)
    print(type(user_data))
    trials_entered = int(user_data['trials'])
    if (type(trials_entered) == int):
        logger.info("Valid integer")
    else:
        logger.info("Invalid integer")

    return ConversationHandler.END

# Two by cancellation
# Function 'cancel' to do that
def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! Hope to see you again.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={

            PAR_1: [CommandHandler('start', start), MessageHandler(Filters.text, par_1)],

            CONFIRMATION: [MessageHandler(Filters.regex('^Confirm$'),confirmation),
                           MessageHandler(Filters.regex('^Restart$'),start)]

            },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    # log all errors
    dp.add_error_handler(error)
	
    PORT = int(os.environ.get('PORT', '8443'))
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))

    
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    #updater.idle()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    #updater.idle()


if __name__ == '__main__':
    main()
