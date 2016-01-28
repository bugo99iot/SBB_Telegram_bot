# -*- coding: utf-8 -*-

from telegram import Updater
import requests
import json
import datetime
from telegram.emoji import Emoji
import telegram

token = '164965900:AAE1_acIuW1lEusHfNrsiGsYVIJWPJOfVcc'
admin = ["jasp215", "FabienS", "psy_s"]

updater = Updater(token=token)

dispatcher = updater.dispatcher


def start(bot, update):
    print update.message.chat.username
    bot.sendMessage(chat_id=update.message.chat_id, text="Hello " + update.message.chat.first_name + ", you can check the current train schedule of SBB-CFF with my help, type /help to see the commands, Bon Voyage!")

def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Use /trains <Departure> <Destination> <Via> to get the next 6 trains from your location, note that 'Via' is optional")

def stop(bot, update):
    if update.message.chat.username in admin:
        updater.stop()

def echo(bot, update):
    t1 = "Yes, "
    t2 = update.message.text
    bot.sendMessage(chat_id=update.message.chat_id, text=t1+t2)


def main():

    dispatcher.addTelegramCommandHandler('start', start)
    dispatcher.addTelegramMessageHandler(echo)
    dispatcher.addTelegramCommandHandler('trains', trains)
    dispatcher.addTelegramCommandHandler('stop', stop)
    dispatcher.addTelegramCommandHandler('help', help)

    updater.start_polling()

def trains(bot, update, args):
    print args

    for i in range(0,len(args)):
        if "heig" in args[i]:
            args[i] = "yverdon"

    if len(args) == 2:
        info = stations(args[0], args[1])
    else:
        info = stations(args[0], args[1], args[2])

    bot.sendMessage(chat_id=update.message.chat_id, text=info,  parse_mode= telegram.ParseMode.MARKDOWN)

# dep = raw_input("Enter your departure location:  ")
# arr = raw_input("Enter your arrival destination:  ")
# via = raw_input("Enter any station you'd like to pass through: ")

def stations(dep_loc, arr_loc, via = ''):
    if via == '':
        url_str = "http://transport.opendata.ch/v1/connections?from=%s&to=%s&limit=6" % (dep_loc, arr_loc)
    else:
        url_str = "http://transport.opendata.ch/v1/connections?from=%s&to=%s&via=%s&limit=6" % (dep_loc, arr_loc, via)

    response = requests.get(url_str)

    r = response.content

    r = json.loads(r)

    res = " "
    for i in range(0,len(r['connections'])):
        timestamp = r['connections'][i]['from']['departureTimestamp']
        timeDep = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M')
        res = res + "Next train from " +r['connections'][i]['from']['location']['name']+ " at *" + timeDep + "* on platform " + r['connections'][i]['from']['platform']

        timestamp = r['connections'][i]['to']['arrivalTimestamp']
        timeArr = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M')
        res = res + " reaching " + r['to']['name']+ " at *" + timeArr + "* on platform " + r['connections'][i]['to']['platform']
        res = res + "\n\n"

    return res


if __name__ == "__main__":
    main()
