from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
import random
import string
from chapa import Chapa
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


CHANNEL = -1001257728396
CHANNEL_USERNAME = 'chapashoping'

chapa = Chapa('CHAPA TEST SECRET KEY',
              response_format='obj')


def create_chapa_checkout(data):
    response = chapa.initialize(**data)
    if response.status != 'success':
        return None

    return response.data


def start(update, context):
    """Send a message when the command /start is issued."""
    # get the command argument
    if update.message.text != '/start':
        cmd = context.args[0]
    else:
        cmd = None
    bot = context.bot
    bot_username = bot.get_me().username
    user = update.effective_user

    if cmd and not cmd.startswith('tx_'):
        try:
            random_tx = "".join(random.choices(string.ascii_letters, k=5))
            random_email = "".join(random.choices(string.ascii_letters, k=5))
            random_domain = "".join(random.choices(string.ascii_letters, k=5))
            data = {
                'email': f"{random_email}@{random_domain}.com",
                'amount': 1000,
                'tx_ref': random_tx,
                'first_name': user.first_name,
                'last_name': user.last_name or ' None',
                'callback_url': f'https://t.me/{bot_username}?start=tx_{random_tx}',
                'customization': {
                    'title': 'Amazing Bot',
                    'description': 'This is a test project for chapa python sdk'
                }
            }
            checkout = create_chapa_checkout(data)
            bot.copy_message(
                chat_id=update.effective_user.id,
                from_chat_id=CHANNEL,
                message_id=cmd
            )
            text = 'You want to buy this item? \n Click the button below to continue'
            keyboard = [[
                InlineKeyboardButton(
                    "Chapa Pay", web_app=WebAppInfo(checkout.checkout_url))
            ]]

            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(
                chat_id=update.effective_user.id,
                text=text,
                reply_markup=reply_markup
            )
            context.user_data[random_tx] = 'PENDING'

            return

        except Exception as e:
            print('Error', e)
    
    if cmd and cmd.startswith('tx_'):
        if context.user_data.get(cmd[3:]) == 'PENDING':
            response = chapa.verify(cmd[3:])
            if response.status == 'success':
                context.user_data[cmd[3:]] = 'SUCCESS'
                bot.send_message(
                    chat_id=update.effective_user.id,
                    text='Your payment was successful'
                )
                return
            else:
                context.user_data[cmd[3:]] = 'FAILED'
                bot.send_message(
                    chat_id=update.effective_user.id,
                    text='Your payment failed'
                )
                return

    update.message.reply_text('Well come to Chapa Shopping! \n\nuse this channel @chapashoping or https://t.me/chapashoping')


def channel_post(update, context):
    # add button to message and send to channel
    url = f'https://t.me/{context.bot.get_me().username}?start={update.channel_post.message_id}'
    keyboard = [[
        InlineKeyboardButton("Buy with Chapa!", url=url)
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_reply_markup(
        chat_id=CHANNEL,
        message_id=update.channel_post.message_id,
        reply_markup=reply_markup
    )


def event(update, context):
    print('Message', update)


def main():
    TOKEN = 'TOKEN'
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    print(updater.bot.get_me())

    dispatcher.add_handler(CommandHandler("start", start))
    #
    dispatcher.add_handler(MessageHandler(
        Filters.chat_type.channel, channel_post))
    # catch all handler
    dispatcher.add_handler(MessageHandler(Filters.all, event))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
