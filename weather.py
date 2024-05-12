import telebot
import requests
import json
from telebot import types
from plausible_events import PlausibleEvents
from os import getenv


events = PlausibleEvents(domain=getenv("PLAUSIBLE_DOMAIN"), api=getenv("PLAUSIBLE_API"))
bot = telebot.TeleBot(getenv("TELEGRAM_API_KEY").strip())
users = set()


@bot.message_handler(commands=['start'])
def start(message):
    users.add(message.from_user.id)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Здесь ты можешь смотреть погоду в любом городе, прямо в Telegram!')
    bot.reply_to(message, 'Cмотреть погоду - введите город🏙 \n/appendcity - добавить город на клавиатуру')
    events.pageview(
        '/',
        headers={
            'X-Forwarded-For': str(message.from_user.id),
        },
    )
    print(len(users))


@bot.message_handler(commands=['appendcity'])
def appen(message):
    bot.send_message(message.chat.id, '⚜️Введите города, которые вы хотите поместить на клавиатуру в 1 сообщении, разделяя пробелами⚜️')
    bot.register_next_step_handler(message, addcity)


def addcity(message):
    cityapp = message.text.split(' ')
    knopka = types.ReplyKeyboardMarkup()
    for city in cityapp:
        knopkacity = types.KeyboardButton(city)
        knopka.row(knopkacity)
        events.event(
            'append',
            path='/',
            headers={
                'X-Forwarded-For': str(message.from_user.id),
            },
            props={
                "city": city,
            },
        )
    bot.send_message(message.chat.id, '<b>Готово!</b>🍃 \nСмотреть погоду - введите город🏙', reply_markup=knopka, parse_mode='html')


@bot.message_handler(content_types='text')
def weather(message):
    city = message.text.strip().lower()
    if city == 'питер':
        city = 'санкт-петербург'
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={getenv("OPENWEATHERMAP_KEY")}&units=metric')
    data = json.loads(res.text)
    try:
        temperature = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        smiletemp = ''
        if feels > 22:
            smiletemp = '🔥'
        elif feels > 15:
            smiletemp = '🌡️'
        elif feels >= 0:
            smiletemp = '🌫'
        elif feels < 0:
            smiletemp = '❄️ '
        smile = ''
        clouds = data['clouds']['all']
        if clouds > 70:
            smile = '☁️ '
        elif clouds > 35:
            smile = "⛅️"
        elif clouds >= 0:
            smile = '☀️ '
        events.event(
            'weather',
            path='/',
            headers={
                'X-Forwarded-For': str(message.from_user.id),
            },
            props={
                "city": city,
            },
        )
        bot.reply_to(message, f'Сейчас погода: {temperature}°C {smile}, ощущается, как {round(feels, 1)}°C{smiletemp}')
    except KeyError:
        bot.send_message(message.chat.id, 'Город введен неправильно, либо я не знаю такого города😕.')


bot.infinity_polling()
