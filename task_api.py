import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENWEATHER_API_KEY")

city = input("Введите название города: ")

url = "https://api.openweathermap.org/data/2.5/weather"

params = {
    "q": city,
    "appid": api_key,
    "units": "metric",
    "lang": "ru"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    weather = response.json()

    print("Город:", city)
    print("Температура:", weather["main"]["temp"], "°C")
    print("Погода:", weather["weather"][0]["description"])
else:
    print("Ошибка:", response.status_code)