# -*- coding: utf-8 -*-

from telegram import Updater
import requests
import json
import datetime
import telegram

token = '164965900:AAE1_acIuW1lEusHfNrsiGsYVIJWPJOfVcc'
admin = ["jasp215", "FabienS", "psy_s"]

updater = Updater(token=token)

dispatcher = updater.dispatcher


def start(bot, update):
    print update.message.chat.username
    t = """Hello %s, you can check the current train schedule of SBB-CFF with my help,
    type /help to see the commands, Bon Voyage!""" % update.message.chat.first_name
    bot.sendMessage(chat_id=update.message.chat_id, text=t)


def help(bot, update):
    t = """Use /trains <Departure> <Destination> <Via> to get next 6 trains
    from your location, note that 'Via' is optional"""
    bot.sendMessage(chat_id=update.message.chat_id, text=t)


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

    for i in range(0, len(args)):
        if "heig" in args[i]:
            args[i] = "yverdon"

    if len(args) == 2:
        info = stations(args[0], args[1])
    else:
        info = stations(args[0], args[1], args[2])

    bot.sendMessage(chat_id=update.message.chat_id, text=info)

def hms_to_minutes(t):
    h, m, s = [int(i) for i in t.split(':')]
    return 60*h + m

def stations(dep_loc, arr_loc, via=''):
    url_str = "http://transport.opendata.ch/v1/connections?from=%s&to=%s"

    if via == '':
        url_str = url_str % (dep_loc, arr_loc)
    else:
        url_str = url_str + "&via=%s" % (dep_loc, arr_loc, via)

    response = requests.get(url_str)

    r = response.content

    r = json.loads(r)
    i = 0
    res = "Connections from " + r['connections'][i]['from']['location']['name'] + " to " + r['to']['name'] + " \n\n"

    nontrains = ["BUS", "M"]

    for i in range(0, len(r['connections'])):

        for j in range(0, len(r['connections'][i]['sections'])):

            if not r['connections'][i]['sections'][j]['walk']:

                timestamp = r['connections'][i]['sections'][j]['departure']['departureTimestamp']
                timeDep = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M')

                timestamp = r['connections'][i]['sections'][j]['arrival']['arrivalTimestamp']
                timeArr = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M')

                if r['connections'][i]['sections'][j]['journey']['category'] in nontrains:
                    res += r['connections'][i]['sections'][j]['departure']['station']['name'] + " [" + timeDep + "] "
                    res += " --> " + r['connections'][i]['sections'][j]['arrival']['station']['name'] + " [" + timeArr + "] "
                    res += " [" + r['connections'][i]['sections'][j]['journey']['category'] + "] \n"
                else:
                    res += r['connections'][i]['sections'][j]['departure']['station']['name'] + " [" + timeDep + "] (P" + r['connections'][i]['sections'][j]['departure']['platform'] + ")"
                    res += " --> " + r['connections'][i]['sections'][j]['arrival']['station']['name'] + " [" + timeArr + "] (P" + r['connections'][i]['sections'][j]['arrival']['platform']  + ")"
                    res += " [" + r['connections'][i]['sections'][j]['journey']['category'] + "] \n"

            else:

                t = r['connections'][i]['sections'][j]['walk']['duration']
                res += "Walk for %d minutes \n" % hms_to_minutes(t)

        res += "\n"

    return res

# Geneva [21:00] (P6) -> Lausanne [21:42] (P2)


# print stations("Bergieres", "Geneva")

if __name__ == "__main__":
    main()
