import webbrowser
import telebot
import requests
import locale
import datetime
from telebot import types

# нужно как-то хранить переменную city именно на этом месте для использования функции get_weather и get_places
# и нужно понять, как эту переменную закидывать в функции

bot = telebot.TeleBot('7181902570:AAGkf7jrLqvhN-pJgvL6NGQr_vE3F1NYTg0')
API = 'dedd8faab24bf4b5adb455980850dc90'


state = {}  # Словарь для хранения состояния и города пользователя
attractions = {}


@bot.message_handler(commands=['start'])
def start(message):
    # начало переписки чата с приветствия
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! 🏖🤘')
    bot.send_message(message.chat.id, 'Рад тебя видеть! Напиши название города.')
    state[message.chat.id] = {'status': 'waiting_for_city'}


@bot.message_handler(func=lambda message: state.get(message.chat.id, {}).get('status') == 'waiting_for_city')
def get_attractions(message):
    city = message.text.strip().lower()
    state[message.chat.id]['city'] = city  # Сохраняем город в состояние пользователя

    url = f'https://ru.wikipedia.org/w/api.php?action=query&list=search&srsearch=достопримечательности+в+{city}&format=json'
    response = requests.get(url)
    data = response.json()

    attractions[message.chat.id] = [(index + 1, item['title'], get_attraction_description(item['title'])) for
                                    index, item in enumerate(data['query']['search'])]

    send_attractions_in_parts(message.chat.id, attractions[message.chat.id])

    bot.send_message(message.chat.id, "Выберите номер достопримечательности для получения подробной информации: ")
    state[message.chat.id]['status'] = 'waiting_for_selection'


def get_attraction_description(attraction_title):
    url = f'https://ru.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={attraction_title}&format=json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        page = next(iter(data['query']['pages'].values()))
        return page.get('extract', '')
    return ''


def send_attractions_in_parts(chat_id, attractions_list):
    attractions_messages = []
    current_message = ""
    for attraction in attractions_list:
        message_line = f"{attraction[0]}. {attraction[1]}\n{attraction[2]}\n\n"
        if len(current_message) + len(message_line) > 4096:
            attractions_messages.append(current_message)
            current_message = message_line
        else:
            current_message += message_line

    if current_message:
        attractions_messages.append(current_message)

    for msg in attractions_messages:
        bot.send_message(chat_id, msg)

def send_attraction_details(chat_id, title):
    # Получение дополнительной информации о достопримечательности
    url = f'https://ru.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={title}&format=json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        page = next(iter(data['query']['pages'].values()))
        extract = page.get('extract', '')
        # Отправка истории, интересных фактов и советов для туристов
        bot.send_message(chat_id, extract)
    else:
        bot.send_message(chat_id, 'Информация о достопримечательности недоступна.')




@bot.message_handler(func=lambda message: state.get(message.chat.id, {}).get('status') == 'waiting_for_selection')
def handle_selection(message):
    try:
        selected_attraction = int(message.text)
        selected_title = attractions[message.chat.id][selected_attraction - 1][1]
        city = state[message.chat.id]['city']  # Используем сохранённый город для запроса погоды

        bot.send_message(message.chat.id, f"Вы выбрали: {selected_title}")
        send_attraction_details(message.chat.id, selected_title)
        send_weather_info(message.chat.id, city)

        state[message.chat.id]['status'] = 'default'


    except Exception as e:
        bot.send_message(message.chat.id, "Пожалуйста, выберите правильный номер достопримечательности.")
        state[message.chat.id]['status'] = 'waiting_for_selection'


def send_weather_info(chat_id, city):
    res = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric&lang=ru')
    if res.status_code == 200:
        data = res.json()
        forecast_message = f"Погода в {city.capitalize()} на 5 дней:\n"
        for item in data['list']:
            forecast_time = datetime.datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
            if forecast_time.hour == 12:  # Выбираем записи, соответствующие полуденному времени
                date = forecast_time.strftime('%Y-%m-%d')
                temperature = item['main']['temp']
                weather_description = item['weather'][0]['description']
                weather_emoji = get_weather_emoji(weather_description)
                forecast_message += f"{date}:  Температура: {temperature}°C, {weather_description.capitalize()} {weather_emoji}\n\n"

        bot.send_message(chat_id, forecast_message)
    else:
        bot.send_message(chat_id, 'Извините, не удалось получить информацию о погоде.')


def get_weather_emoji(weather_description):
    if 'облачно' in weather_description:
        return '☁️'
    elif 'пасмурно' in weather_description:
        return '☁️'
    elif 'ясно' in weather_description:
        return '☀️'
    elif 'дождь' in weather_description:
        return '🌧️'
    elif 'снег' in weather_description:
        return '🌨️'
    elif 'туман' in weather_description:
        return '🌫️'
    else:
        return '🌈'



bot.polling(none_stop=True)

