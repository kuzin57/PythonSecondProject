import telebot
import requests
import time
import datetime
from threading import Thread


class Forecast:
    def __init__(self):
        self.city = ""
        self.days = 0
        pass

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
            ans += i['weather'][0]['description']
            ans += '\n'
        return ans


bot = telebot.TeleBot('5309926111:AAFL8ZQOaWn9txjSg7AoGINXAUptB7fK5l8')
users_id = set()
waiting_for_city = False
waiting_for_days = False
waiting_for_time = False
waiting_for_city_for_every_day_mailing = False
send_forecast = False
forecast_sent = False
time_of_every_day_mailing = "09:00"
city_of_every_day_mailing = "Moscow"
forecaster = Forecast()

# @bot.message_handler(commands=['start'])
# def start_messaging(message):
#     bot.send_message(message.from_user.id, 'Type \'Hi\' to start messaging with me')

# @bot.message_handler(commands=['Set time'])
# def set_time(message):
#     bot.send_message(message.from_user.id, 'Enter time')

# @bot.message_handler(commands=['Set city'])
# def set_city(message):
#     bot.send_message(message.from_user.id, 'Enter city')

@bot.message_handler(content_types=['text'])
def get_text_message(message):
    global waiting_for_city
    global waiting_for_days
    global send_forecast
    global forecaster
    global waiting_for_time
    global time_of_every_day_mailing
    global city_of_every_day_mailing
    global waiting_for_city_for_every_day_mailing
    if message.text == "Hi":
        if message.from_user.id not in users_id:
            users_id.add(message.from_user.id)
        print(users_id)
        bot.send_message(message.from_user.id, "Hi, how can I help you?")
        bot.send_message(message.from_user.id, "Send \'Help\' message to know how to get the forecast")
    elif message.text == "Get weather":
        bot.send_message(message.from_user.id, "One second")
        bot.send_message(message.from_user.id, "Enter the city")
        waiting_for_city = True
    elif waiting_for_city:
        forecaster.set_city(message.text)
        waiting_for_city = False
        bot.send_message(message.from_user.id, "Days(0-5)")
        waiting_for_days = True
    elif waiting_for_days:
        waiting_for_days = False
        forecaster.set_days(int(message.text))
        bot.send_message(message.from_user.id, "Ok")
        send_forecast = True
    elif message.text == "Help":
        bot.send_message(message.from_user.id, "To get forecast -- Get weather\n To thank bot -- Thank you\n To set time of every day forecast mailing -- Set time \n To set city of every day forecast mailing -- Set city")
    elif message.text == 'Thank you':
        bot.send_message(message.from_user.id, 'You are welcome!')
    elif message.text == 'Set time':
        waiting_for_time = True
        bot.send_message(message.from_user.id, "Enter time")
    elif waiting_for_time:
        waiting_for_time = False
        time_of_every_day_mailing = str(message.text)
    elif message.text == 'Set city':
        waiting_for_city_for_every_day_mailing = True
        bot.send_message(message.from_user.id, 'Enter city')
    elif waiting_for_city_for_every_day_mailing:
        waiting_for_city_for_every_day_mailing = False
        city_of_every_day_mailing = str(message.text)
    else:
        bot.send_message(message.from_user.id, 'Sorry, I do not understand you')
    if send_forecast:
        forecast = forecaster.get_forecast()
        bot.send_message(message.from_user.id, forecast)
        send_forecast = False


def send_every_day_forecast():
    forecaster.set_days(1)
    forecaster.set_city(city_of_every_day_mailing)
    forecast = forecaster.get_forecast()
    for id in users_id:
        bot.send_message(id, forecast)
    return True


def every_day_forecasts_managing():
    global forecast_sent
    while True:
        cur_time = str(datetime.datetime.now())
        if(cur_time[:5] == time_of_every_day_mailing and not forecast_sent and len(users_id) > 0):
            forecast_sent = True
            send_every_day_forecast()
        if(cur_time[:5] == '00:00'):
            forecast_sent = False
        time.sleep(1)


Thread(target=every_day_forecasts_managing, args=()).start() 
bot.polling(none_stop=True, interval=0)