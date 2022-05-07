import telebot
import requests
import time
import datetime
from threading import Thread


class Forecast:
    def __init__(self):
        self.city = ""
        self.days = 0

    def set_city(self, city):
        self.city = city

    def set_days(self, days):
        self.days = days

    def get_forecast(self):
        appid = "6575543f67d0febf5c073a6cb368b707"
        res = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={'q': self.city, 'type': 'like', 'units': 'metric', 'APPID': appid})
        data = res.json()
        cur_date = ''
        prev_date = ''
        counter = 0
        ans = ''
        flag = False
        if 'list' not in data:
            return 'Unknown city'
        for i in data['list']:
            prev_date = cur_date
            cur_date = i['dt_txt'].split()[0]
            flag = False
            if cur_date != prev_date:
                flag = True
                counter += 1
            if(counter > self.days):
                break
            if cur_date != prev_date:
                ans += cur_date
                ans += ' '
            if not flag:
                ans += '                     '
            ans += i['dt_txt'].split()[1]
            ans += ' '
            ans += '{0:+3.0f}'.format(i['main']['temp'])
            ans += ' '
            if i['weather'][0]['description'] == 'clear sky':
                ans += '☀️'
            elif i['weather'][0]['description'] == 'few clouds':
                ans += '🌤'
            elif i['weather'][0]['description'] == 'light rain':
                ans += '🌦'
            elif i['weather'][0]['description'] == 'scattered clouds':
                ans += '⛅️'
            elif i['weather'][0]['description'] == 'broken clouds':
                ans += '⛅️'
            elif i['weather'][0]['description'] == 'overcast clouds':
                ans += '☁️'
            elif i['weather'][0]['description'] == 'light snow':
                ans += '🌨'
            elif i['weather'][0]['description'] == 'snow':
                ans += '🌨'
            elif i['weather'][0]['description'] == 'moderate rain':
                ans += '🌧'
            elif i['weather'][0]['description'] == 'rain':
                ans += '🌧'
            else:
                ans += i['weather'][0]['description']
            # ans += i['weather'][0]['description']
            ans += '\n'
        return ans

    def func_for_testing(self, a, b):
        return a + b


class User:
    def __init__(self):
        self.id = 0
        self.city = "Moscow"
        self.time = "09:00"
        self.forecast_sent = False
        self.waiting_for_city = False
        self.waiting_for_days = False
        self.waiting_for_time = False
        self.waiting_for_city_for_every_day_mailing = False

    def set_time(self, t):
        self.time = t

    def set_city(self, city):
        self.city = city

    def set_id(self, new_id):
        self.id = new_id

    def change_forecast_sent(self, is_sent):
        self.forecast_sent = is_sent

    def return_hello(self):
        return 'hello'


bot = telebot.TeleBot('5309926111:AAFL8ZQOaWn9txjSg7AoGINXAUptB7fK5l8')
users = dict()

@bot.message_handler(commands=['start'])
def start_messaging(message):
    global users
    bot.send_message(message.from_user.id, 'Hi!')
    new_user = User()
    new_user.set_id(message.from_user.id)
    users[message.from_user.id] = new_user

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, 'This bot is for getting forecasts, \n you can see the list of commands in menu. \n Send \' /start \' before giving commands')

@bot.message_handler(commands=['get'])
def get(message):
    global users
    bot.send_message(message.from_user.id, "Enter the city")
    if message.from_user.id in users:
        users[message.from_user.id].waiting_for_city = True

@bot.message_handler(commands=['set_time'])
def set_time_of_every_day_mailing(message):
    global users
    if message.from_user.id in users:
        bot.send_message(message.from_user.id, 'Choose the suitable time when I can send you daily forecast \n Format: hh:mm')
        users[message.from_user.id].waiting_for_time = True
        users[message.from_user.id].forecast_sent = False

@bot.message_handler(commands=['set_city'])
def set_city_of_every_day_mailing(message):
    global users
    if message.from_user.id in users:
        bot.send_message(message.from_user.id, 'Choose the city which weather you are interested in every day')
        users[message.from_user.id].waiting_for_city_for_every_day_mailing = True

@bot.message_handler(commands=['thank_you'])
def thank_from_user(message):
    bot.send_message(message.from_user.id, 'You are welcome 😍')


@bot.message_handler(content_types=['text'])
def get_info_from_user(message):
    global users
    if message.from_user.id in users:
        if users[message.from_user.id].waiting_for_city:
            users[message.from_user.id].waiting_for_city = False
            users[message.from_user.id].set_city(message.text)
            bot.send_message(message.from_user.id, 'Days (1-5)')
            users[message.from_user.id].waiting_for_days = True
        elif users[message.from_user.id].waiting_for_days:
            users[message.from_user.id].waiting_for_days = False
            forecaster = Forecast()
            forecaster.set_days(int(message.text))
            forecaster.set_city(users[message.from_user.id].city)
            forecast = forecaster.get_forecast()
            bot.send_message(message.from_user.id, forecast)
        elif users[message.from_user.id].waiting_for_time:
            users[message.from_user.id].waiting_for_time = False
            users[message.from_user.id].set_time(message.text)
        elif users[message.from_user.id].waiting_for_city_for_every_day_mailing:
            users[message.from_user.id].waiting_for_city_for_every_day_mailing = False
            users[message.from_user.id].set_city(message.text)


def send_every_day_forecast(user_id):
    global users
    forecaster = Forecast()
    forecaster.set_days(1)
    forecaster.set_city(users[user_id].city)
    forecast = forecaster.get_forecast()
    bot.send_message(user_id, forecast)
    return True


def every_day_forecasts_managing():
    global users
    while True:
        for i in users:
            cur_time = str(datetime.datetime.now().time())
            if cur_time[:5] == users[i].time and not users[i].forecast_sent:
                users[i].change_forecast_sent(True)
                send_every_day_forecast(users[i].id)
            if(cur_time[:5] == '00:00'):
                users[i].forecast_sent = False
        time.sleep(1)


Thread(target=every_day_forecasts_managing).start()
bot.polling(none_stop=True, interval=0)