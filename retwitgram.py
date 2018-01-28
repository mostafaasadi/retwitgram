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

# bot logo address
logo_address = "http://domain/retwittgram.png"

api = tweepy.API(
    auth,
    wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True,
    retry_count=2,
    retry_delay=2,
    compression=True
)

# Telegram API
# access  bot via token
updater = Updater(token='Telegram HTTP API Token')
dispatcher = updater.dispatcher


# extend and get tweet
def extend(link):
    global tweet, extend_status
    id = link.split('/')[-1].split('?')[0]
    try:
        tweet = api.get_status(id, tweet_mode='extended')
        extend_status = True
    except Exception:
        print('Error on extend')
        extend_status = False

    return tweet, extend_status


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
    bot.send_chat_action(
        chat_id=update.message.chat_id,
        action=ChatAction.TYPING)

    try:
        link = re.search(
            '(?P<url>https?://[^\s]+)',
            update.message.text).group('url').split('?')[0]
    except Exception:
        bot.send_message(
            chat_id=update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            text='❌'
        )

    extend(link)
    if extend_status:
        pure_text = re.sub(r"http\S+", '', tweet.full_text)
        kb = [
            [InlineKeyboardButton(text='🔗', url=str(link)),
                InlineKeyboardButton(text='ℹ️', callback_data=str(link)),
                InlineKeyboardButton(text='🔀', switch_inline_query=str(link))]
        ]
        if tweet.is_quote_status:
            response = pure_text + '\n\n' + '           💬' + '  ' + \
                tweet.quoted_status['user']['name'] + ' : ' + \
                tweet.quoted_status['full_text'] + \
                ' \n\n 👤 <a href=\"' + link + '\">' + tweet.user.name + '</a>'

        else:
            response = tweet.full_text + ' \n\n 👤 <a href=\"' + \
                link + '\">' + tweet.user.name + '</a>'
        if 'media' in tweet.entities:
            if (
                    tweet.entities['media'][0]['type'] == 'photo' and
                    not tweet.extended_entities['media'][0]['type'] == 'video'
            ):
                response = pure_text + ' \n\n 👤 ' + tweet.user.name + \
                    '\n ' + tweet.entities['media'][0]['url']
                if len(response) > 200:
                    response = '<a href=\"' + \
                        tweet.entities['media'][0]['media_url_https'] + \
                        '\">&#8205;</a> ' + pure_text + ' \n\n 👤 ' + \
                        tweet.user.name + '\n ' +\
                        tweet.entities['media'][0]['url']
                    bot.send_message(
                        parse_mode='HTML',
                        chat_id=update.message.chat_id,
                        reply_markup=InlineKeyboardMarkup(
                            kb,
                            resize_keyboard=True),
                        reply_to_message_id=update.message.message_id,
                        text=response
                    )
                else:
                    bot.sendPhoto(
                        photo=tweet.entities['media'][0]['media_url'],
                        chat_id=update.message.chat_id,
                        reply_markup=InlineKeyboardMarkup(
                            kb,
                            resize_keyboard=True),
                        reply_to_message_id=update.message.message_id,
                        caption=response
                    )

            if tweet.extended_entities['media'][0]['video_info']['variants'][0]['content_type'] == 'video/mp4':
                response = pure_text + ' \n\n 👤 ' + tweet.user.name + \
                    '\n ' + tweet.entities['media'][0]['url']
                if len(response) > 200:
                    response = '<a href=\"' + \
                        tweet.extended_entities['media'][0]['video_info']['variants'][0]['url'] + \
                        '\">&#8205;</a> ' + pure_text + ' \n\n 👤 ' + \
                        tweet.user.name + '\n ' +\
                        tweet.entities['media'][0]['url']
                    bot.send_message(
                        parse_mode='HTML',
                        chat_id=update.message.chat_id,
                        reply_markup=InlineKeyboardMarkup(
                            kb,
                            resize_keyboard=True),
                        reply_to_message_id=update.message.message_id,
                        text=response
                    )
                else:
                    bot.send_video(
                        video=tweet.extended_entities['media'][0]['video_info']['variants'][0]['url'],
                        chat_id=update.message.chat_id,
                        reply_markup=InlineKeyboardMarkup(
                            kb,
                            resize_keyboard=True),
                        reply_to_message_id=update.message.message_id,
                        caption=response
                    )
            elif tweet.extended_entities['media'][0]['video_info']['variants'][1]['content_type'] == 'video/mp4':
                response = pure_text + ' \n\n 👤 ' + tweet.user.name + \
                    '\n ' + tweet.entities['media'][0]['url']
                if len(response) > 200:
                    response = '<a href=\"' + \
                        tweet.extended_entities['media'][0]['video_info']['variants'][1]['url'] + \
                        '\">&#8205;</a> ' + pure_text + ' \n\n 👤 ' + \
                        tweet.user.name + '\n ' +\
                        tweet.entities['media'][0]['url']
                    bot.send_message(
                        parse_mode='HTML',
                        chat_id=update.message.chat_id,
                        reply_markup=InlineKeyboardMarkup(
                            kb,
                            resize_keyboard=True),
                        reply_to_message_id=update.message.message_id,
                        text=response
                    )
                else:
                    bot.send_video(
                        video=tweet.extended_entities['media'][0]['video_info']['variants'][1]['url'],
                        chat_id=update.message.chat_id,
                        reply_markup=InlineKeyboardMarkup(
                            kb,
                            resize_keyboard=True),
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
    if not extend_status:
        bot.send_message(
            chat_id=update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            text='❌'
        )


# inline respond function
def inlinequery(bot, update):
    results = list()
    results.clear()
    # inline mode for zero character
    if len(update.inline_query.query) <= 5:
        results.clear()

        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title=" ▶️ Retwittgram",
            description="type tweet link",
            url="https://twitter.com/user/status/9876543210",
            thumb_url=logo_address,
            input_message_content=InputTextMessageContent(
                " ♻️ @retwitgrambot sends your tweet beautifully ")))

    # inline mode in normal case
    else:
        link = re.search(
            '(?P<url>https?://[^\s]+)',
            update.inline_query.query).group('url').split('?')[0]

        extend(link)
        pure_text = re.sub(r"http\S+", '', tweet.full_text)

        if extend_status:
            if tweet.is_quote_status:
                response = pure_text + '\n\n' + '           💬' + '  ' + \
                    tweet.quoted_status['user']['name'] + ' : ' + \
                    tweet.quoted_status['full_text'] + ' \n\n 👤 <a href=\"' + \
                    link + '\">' + tweet.user.name + '</a>'

            else:
                response = tweet.full_text + ' \n\n 👤 <a href=\"' + link + \
                    '\">' + tweet.user.name + '</a>'

            kb = [
                [InlineKeyboardButton(text='🔗', url=link),
                    InlineKeyboardButton(text='ℹ️', callback_data=link),
                    InlineKeyboardButton(text='🔀', switch_inline_query=link)]
            ]

            if 'media' in tweet.entities:
                if (
                        tweet.entities['media'][0]['type'] == 'photo' and
                        not tweet.extended_entities['media'][0]['type'] == 'video'
                ):
                    response = pure_text + ' \n\n 👤 ' + tweet.user.name + \
                        '\n ' + tweet.entities['media'][0]['url']
                    if len(response) > 200:
                        response = '<a href=\"' + \
                            tweet.entities['media'][0]['media_url_https'] + \
                            '\">&#8205;</a> ' + pure_text + ' \n\n 👤 ' + \
                            tweet.user.name + '\n ' + \
                            tweet.entities['media'][0]['url']
                        results.append(InlineQueryResultArticle(
                            id=uuid4(),
                            title=tweet.user.name,
                            description=tweet.full_text,
                            url=link,
                            thumb_url=tweet.entities['media'][0]['url'],
                            reply_markup=InlineKeyboardMarkup(
                                kb,
                                resize_keyboard=True),
                            input_message_content=InputTextMessageContent(
                                response,
                                parse_mode=ParseMode.HTML)))

                    else:
                        results.append(InlineQueryResultPhoto(
                            id=uuid4(),
                            type='photo',
                            photo_url=tweet.entities['media'][0]['media_url'],
                            thumb_url=tweet.entities['media'][0]['media_url'],
                            title=tweet.user.name,
                            description=pure_text,
                            caption=response,
                            reply_markup=InlineKeyboardMarkup(
                                kb,
                                resize_keyboard=True)
                        ))
                if tweet.extended_entities['media'][0]['video_info']['variants'][0]['content_type'] == 'video/mp4':
                    response = pure_text + ' \n\n 👤 ' + tweet.user.name + \
                        '\n ' + tweet.entities['media'][0]['url']
                    response = '<a href=\"' + \
                        tweet.extended_entities['media'][0]['video_info']['variants'][0]['url'] + \
                        '\">&#8205;</a> ' + pure_text + ' \n\n 👤 ' + \
                        tweet.user.name + '\n ' +\
                        tweet.entities['media'][0]['url']
                    results.append(InlineQueryResultArticle(
                        id=uuid4(),
                        title=tweet.user.name,
                        description=tweet.full_text,
                        url=link,
                        thumb_url=tweet.entities['media'][0]['url'],
                        reply_markup=InlineKeyboardMarkup(
                            kb,
                            resize_keyboard=True),
                        input_message_content=InputTextMessageContent(
                            response,
                            parse_mode=ParseMode.HTML)))

                elif tweet.extended_entities['media'][0]['video_info']['variants'][1]['content_type'] == 'video/mp4':
                    response = '<a href=\"' + \
                        tweet.extended_entities['media'][0]['video_info']['variants'][1]['url'] + \
                        '\">&#8205;</a> ' + pure_text + ' \n\n 👤 ' + \
                        tweet.user.name + '\n ' +\
                        tweet.entities['media'][0]['url']
                    results.append(InlineQueryResultArticle(
                        id=uuid4(),
                        title=tweet.user.name,
                        description=tweet.full_text,
                        url=link,
                        thumb_url=tweet.entities['media'][0]['url'],
                        reply_markup=InlineKeyboardMarkup(
                            kb,
                            resize_keyboard=True),
                        input_message_content=InputTextMessageContent(
                            response,
                            parse_mode=ParseMode.HTML)))

        if not extend_status:
            results.append(InlineQueryResultArticle(
                id=uuid4(),
                title=" ▶️ Retwittgram",
                description="❌",
                url="https://twitter.com/user/status/9876543210",
                thumb_url=logo_address,
                input_message_content=InputTextMessageContent(
                    " ♻️ @retwitgrambot sends your tweet beautifully ")))
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


if __name__ == '__main__':
    main()
