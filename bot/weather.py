import requests

from config import API_KEY


def get_current_weather(latitude, longitude):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric&lang=ru'
    response = requests.get(url)
    return response.json()


def get_weather_forecast(latitude, longitude):
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric&lang=ru'
    response = requests.get(url)
    return response.json()


def convert_month(month):
    months = {
        "January": "января",
        "February": "февраля",
        "March": "марта",
        "April": "апреля",
        "May": "мая",
        "June": "июня",
        "July": "июля",
        "August": "августа",
        "September": "сентября",
        "October": "октября",
        "November": "ноября",
        "December": "декабря"
    }
    return months.get(month, month)
