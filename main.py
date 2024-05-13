import webbrowser
import telebot
import requests
import json
import datetime
from telebot import types

# нужно как-то хранить переменную city именно на этом месте для использования функции get_weather и get_places
# и нужно понять, как эту переменную закидывать в функции

bot = telebot.TeleBot('7181902570:AAGkf7jrLqvhN-pJgvL6NGQr_vE3F1NYTg0')
API = 'dedd8faab24bf4b5adb455980850dc90'

@bot.message_handler(commands=['start'])
def start(message):
    # начало переписки чата с приветствия
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! 🏖🤘')
    bot.send_message(message.chat.id, 'Рад тебя видеть! Напиши название города')



@bot.message_handler(content_types=['text'])
# def get_place(message):
#     global city
#     city = message.text.strip().lower()
#
#
#
#
#
#     bot.register_next_step_handler(message, get_weather)


def get_weather(message):
    city = message.text.strip().lower()

    res = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        #data = json.loads(res.text)

        # Преобразуем ответ в JSON
        data = res.json()

        # Получаем текущую дату
        current_date = datetime.datetime.now().date()

        # Инициализируем переменные для хранения данных о погоде
        forecast_data = []

    # Обрабатываем данные из ответа
        for item in data["list"]:
            # Извлекаем дату из времени
            forecast_date = datetime.datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S").date()

            # Проверяем, является ли дата следующим днем и время 12:00:00
            if forecast_date > current_date and item["dt_txt"].endswith("12:00:00"):
                # Извлекаем температуру
                temperature = item["main"]["temp"]

                # Извлекаем тип погоды
                weather_type = item["weather"][0]["main"]

                # Добавляем данные в список
                forecast_data.append({
                    "date": forecast_date,
                    "temperature": temperature,
                    "weather_type": weather_type
                })



        # Выводим полученные данные
        if forecast_data:
            for data in forecast_data:
                if data["weather_type"] == 'Clouds':
                    emojy = '☁️'
                elif data["weather_type"] == 'Sunny' or data["weather_type"] == 'Clear':
                    emojy = '☀️'
                elif data["weather_type"] == 'Rain':
                    emojy = '🌧'
                elif data["weather_type"] == 'Snow':
                    emojy = '🌨'
                bot.reply_to(message,f"Погода на {data["date"]}\nТемпература: {data["temperature"]} °C\nТип погоды: {data["weather_type"]}")
                bot.send_message(message.chat.id, emojy)

    else:
        bot.reply_to(message, 'Город указан не верно')






bot.polling(none_stop=True)

