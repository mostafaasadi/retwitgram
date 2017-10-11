import tweepy
import re
from uuid import uuid4
from telegram.ext import Updater, CommandHandler, MessageHandler, \
    Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent, ChatAction

# Twitter API
auth = tweepy.OAuthHandler(
    'consumer_token',
    'consumer_secret')
auth.set_access_token(
    'key',
    'secret')

api = tweepy.API(auth)

# Telegram API
# access  bot via token
updater = Updater(token='HTTP API')
dispatcher = updater.dispatcher


def filewrite(filename, mode, string):
    f = open(filename, mode)
    f.write(str(string))
    f.close()


# extend and get tweet
def extend(link):
    global tweet
    id = link.split('/')[-1]
    try:
        tweet = api.get_status(id)
    except Exception:
        print('Error on extend tweets')
    filewrite('retwittgrambot', 'a', tweet.user.name + '\n')
    return tweet


def start(bot, update):
    update.message.reply_text('Hi , send me tweet link')
    return directresponse


# direct chat
def directresponse(bot, update):
    msg = update.message.text
    bot.send_chat_action(
        chat_id=update.message.chat_id,
        action=ChatAction.TYPING)
    link = re.search("(?P<url>https?://[^\s]+)", msg).group('url')
    extend(link)

    # response = tweet.text + ' \n\n 👤 <a href=\"' + link + '\">' + \
    #     tweet.user.name + '</a>'

    if tweet.is_quote_status:
        response = tweet.text + '\n\n' + '           💬' + '  ' + \
            tweet.quoted_status['user']['name'] + ' : ' + \
            tweet.quoted_status['text'] + \
            ' \n\n 👤 <a href=\"' + link + '\">' + tweet.user.name + '</a>'
    else:
        response = tweet.text + ' \n\n 👤 <a href=\"' + link + '\">' + \
            tweet.user.name + '</a>'

    bot.sendMessage(
        parse_mode='HTML',
        disable_web_page_preview=True,
        chat_id=update.message.chat_id,
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
            thumb_url="http://domain/retwittgram.png",
            input_message_content=InputTextMessageContent(
                " ♻️ @retwitgrambot sends your tweet beautifully ")))

    # inline mode in normal case
    else:
        tweet = extend(link)

        if tweet.is_quote_status:
            response = tweet.text + '\n\n' + '           💬' + '  ' + \
                tweet.quoted_status['user']['name'] + ' : ' + \
                tweet.quoted_status['text'] + \
                ' \n\n 👤 <a href=\"' + link + '\">' + tweet.user.name + '</a>'
        else:
            response = tweet.text + ' \n\n 👤 <a href=\"' + link + '\">' + \
                tweet.user.name + '</a>'

        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title=tweet.user.name,
            description=tweet.text,
            url=link,
            thumb_url=tweet.user.profile_image_url_https,
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
        document='BQADBAADkgEAAnSB8FIc_ncoMlDLZwI')


def main():
    # handlers
    start_handler = CommandHandler('start', start)
    second_handler = MessageHandler(Filters.text, directresponse)
    cancel_handler = CommandHandler('cancel', cancel)
    about_handler = CommandHandler('about', about)
    help_handler = CommandHandler('help', helpf)

    # handle dispatcher
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
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
