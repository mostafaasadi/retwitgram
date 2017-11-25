import tweepy
import re
from uuid import uuid4
from telegram.ext import Updater, CommandHandler, MessageHandler, \
    Filters, InlineQueryHandler, CallbackQueryHandler
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent, ChatAction, InlineKeyboardMarkup, \
    InlineKeyboardButton, InlineQueryResultPhoto

# Twitter API
auth = tweepy.OAuthHandler(
    'consumer_token',
    'consumer_secret')
auth.set_access_token(
    'key',
    'secret')


api = tweepy.API(
    auth,
    wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)

# Telegram API
# access  bot via token
updater = Updater(token='HTTP API')
dispatcher = updater.dispatcher


# extend and get tweet
def extend(link):
    global tweet
    id = link.split('/')[-1]
    try:
        tweet = api.get_status(id, tweet_mode='extended')
    except Exception:
        print('Error on extend tweets')
    return tweet


def start(bot, update):
    update.message.reply_text('Hi , send me tweet link')
    return directresponse


def button(bot, update):
    extend(update.callback_query.data)
    callback_res = '❤️ : ' + str(tweet.favorite_count) + '      🔁 : ' + \
        str(tweet.retweet_count)

    bot.answerCallbackQuery(
        callback_query_id=update.callback_query.id,
        text=callback_res)


# direct chat
def directresponse(bot, update):
    global link
    msg = update.message.text
    bot.send_chat_action(
        chat_id=update.message.chat_id,
        action=ChatAction.TYPING)
    link = re.search("(?P<url>https?://[^\s]+)", msg).group('url')
    extend(link)
    kb = [
        [InlineKeyboardButton(text='🔗', url=link),
            InlineKeyboardButton(text='ℹ️', callback_data=link),
            InlineKeyboardButton(text='🔀', switch_inline_query=str(link))]
    ]
    if tweet.is_quote_status:
        pure_text = re.sub(r"http\S+", '', tweet.full_text)
        response = pure_text + '\n\n' + '           💬' + '  ' + \
            tweet.quoted_status['user']['name'] + ' : ' + \
            tweet.quoted_status['full_text'] + \
            ' \n\n 👤 <a href=\"' + link + '\">' + tweet.user.name + '</a>'

    else:
        response = tweet.full_text + ' \n\n 👤 <a href=\"' + link + '\">' + \
            tweet.user.name + '</a>'

    if 'media' in tweet.entities:
        if tweet.entities['media'][0]['type'] == 'photo':
            pure_text = re.sub(r"http\S+", '', tweet.full_text)
            response = pure_text + ' \n\n 👤 ' + tweet.user.name + \
                '\n ' + tweet.entities['media'][0]['url']
            bot.sendPhoto(
                photo=tweet.entities['media'][0]['media_url_https'],
                chat_id=update.message.chat_id,
                reply_markup=InlineKeyboardMarkup(kb, resize_keyboard=True),
                reply_to_message_id=update.message.message_id,
                caption=response
            )
    else:
        bot.send_message(
            parse_mode='HTML',
            disable_web_page_preview=True,
            chat_id=update.message.chat_id,
            reply_markup=InlineKeyboardMarkup(kb, resize_keyboard=True),
            reply_to_message_id=update.message.message_id,
            text=response
        )


# inline respond function
def inlinequery(bot, update):
    results = list()
    link = update.inline_query.query
    results.clear()

    # inline mode for zero character
    if len(link) == 0:
        results.clear()

        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title=" ▶️ Retwittgram",
            description="type tweet link",
            url="https://twitter.com/user/status/9876543210",
            thumb_url="http://ip/retwittgram.png",
            input_message_content=InputTextMessageContent(
                " ♻️ @retwitgrambot sends your tweet beautifully ")))

    # inline mode in normal case
    else:
        tweet = extend(link)

        if tweet.is_quote_status:
            pure_text = re.sub(r"http\S+", '', tweet.full_text)
            response = pure_text + '\n\n' + '           💬' + '  ' + \
                tweet.quoted_status['user']['name'] + ' : ' + \
                tweet.quoted_status['full_text'] + \
                ' \n\n 👤 <a href=\"' + link + '\">' + tweet.user.name + '</a>'

        else:
            response = tweet.full_text + ' \n\n 👤 <a href=\"' + link + \
                '\">' + tweet.user.name + '</a>'

        kb = [
            [InlineKeyboardButton(text='🔗', url=link),
                InlineKeyboardButton(text='ℹ️', callback_data=link),
                InlineKeyboardButton(text='🔀', switch_inline_query=str(link))]
        ]

        if 'media' in tweet.entities:
            if tweet.entities['media'][0]['type'] == 'photo':
                pure_text = re.sub(r"http\S+", '', tweet.full_text)
                response = pure_text + ' \n\n 👤 ' + tweet.user.name + \
                    '\n ' + tweet.entities['media'][0]['url']
                results.append(InlineQueryResultPhoto(
                    id=uuid4(),
                    type='photo',
                    photo_url=tweet.entities['media'][0]['media_url_https'],
                    thumb_url=tweet.entities['media'][0]['media_url_https'],
                    title=tweet.user.name,
                    description=pure_text,
                    caption=response,
                    reply_markup=InlineKeyboardMarkup(kb, resize_keyboard=True)
                ))
        else:
            results.append(InlineQueryResultArticle(
                id=uuid4(),
                title=tweet.user.name,
                description=tweet.full_text,
                url=link,
                thumb_url=tweet.user.profile_image_url_https,
                reply_markup=InlineKeyboardMarkup(kb, resize_keyboard=True),
                input_message_content=InputTextMessageContent(
                    response,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True)))

    # update inline respond
    update.inline_query.answer(results)


# cancel function
def cancel(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="canceled")


# About function
def about(bot, update):
    abouttext = "  ♻️ @retwitgrambot sends your tweet beautifully \n" + \
        "🔗 https://github.com/mostafaasadi/retwitgram"
    bot.sendMessage(chat_id=update.message.chat_id, text=abouttext)


# help function
def helpf(bot, update):
    bot.sendChatAction(
        chat_id=update.message.chat_id,
        action=ChatAction.RECORD_VIDEO)
    bot.sendChatAction(
        chat_id=update.message.chat_id,
        action=ChatAction.UPLOAD_VIDEO)
    bot.sendDocument(
        chat_id=update.message.chat_id,
        document='CgADBAADzgEAAhvd8FLkIjsOlU6tlwI')


def main():
    # handlers
    start_handler = CommandHandler('start', start)
    second_handler = MessageHandler(Filters.text, directresponse)
    cancel_handler = CommandHandler('cancel', cancel)
    about_handler = CommandHandler('about', about)
    help_handler = CommandHandler('help', helpf)

    # handle dispatcher
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(second_handler)
    dispatcher.add_handler(about_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(cancel_handler)

    # run
    updater.start_polling()
    updater.idle()
    updater.stop()


if __name__ == '__main__':
    main()
