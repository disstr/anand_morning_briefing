# -*- coding: utf-8 -*-
"""
Өглөөний мэдээ: Улаанбаатарын цаг агаар + XAUUSD (Gold futures) -> Telegram
GitHub Actions дээр ажиллуулах хувилбар - token/chat_id-г Secrets-ээс уншина.
"""

import os
import requests
import yfinance as yf
from datetime import datetime

# ============ ТОХИРГОО ============
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# Улаанбаатарын координат
LAT, LON = 47.92, 106.92

WEATHER_CODES = {
    0: "Цэлмэг ☀️", 1: "Багавтар үүлтэй 🌤", 2: "Үүлэрхэг ⛅", 3: "Бүрхэг ☁️",
    45: "Манантай 🌫", 48: "Хөлдүү манантай 🌫",
    51: "Шиврээ бороо 🌦", 53: "Шиврээ бороо 🌦", 55: "Шиврээ бороо 🌧",
    61: "Бага зэргийн бороо 🌧", 63: "Бороо 🌧", 65: "Аадар бороо ⛈",
    71: "Бага зэргийн цас 🌨", 73: "Цас 🌨", 75: "Их цас ❄️",
    80: "Үе үе бороо 🌦", 81: "Үе үе бороо 🌧", 82: "Ширүүн бороо ⛈",
    85: "Үе үе цас 🌨", 86: "Их цас ❄️",
    95: "Аянга цахилгаантай ⛈", 96: "Мөндөртэй аадар ⛈", 99: "Мөндөртэй аадар ⛈",
}


def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code,"
                 "precipitation_probability_max",
        "timezone": "Asia/Ulaanbaatar",
        "forecast_days": 1,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    cur = data["current"]
    day = data["daily"]

    now_text = (
        f"🌡 Одоо: {cur['temperature_2m']}°C "
        f"(мэдрэгдэх нь {cur['apparent_temperature']}°C)\n"
        f"{WEATHER_CODES.get(cur['weather_code'], 'Тодорхойгүй')}, "
        f"салхи {cur['wind_speed_10m']} км/ц"
    )
    day_text = (
        f"📅 Өнөөдөр: {day['temperature_2m_min'][0]}°C ... "
        f"{day['temperature_2m_max'][0]}°C\n"
        f"{WEATHER_CODES.get(day['weather_code'][0], 'Тодорхойгүй')}, "
        f"хур тунадасны магадлал {day['precipitation_probability_max'][0]}%"
    )
    return now_text, day_text


def get_gold():
    try:
        ticker = yf.Ticker("GC=F")
        hist = ticker.history(period="5d", interval="1d")
        if hist.empty:
            return "🥇 XAUUSD (Gold futures): дата олдсонгүй"
        price = hist["Close"].iloc[-1]
        return f"🥇 XAUUSD (Gold futures): ${price:,.2f}"
    except Exception as e:
        return f"🥇 XAUUSD: авч чадсангүй ({e})"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    r = requests.post(url, data=payload, timeout=15)
    r.raise_for_status()


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    parts = [f"<b>🌅 Өглөөний мэдээ — {today}</b>", ""]

    try:
        now_text, day_text = get_weather()
        parts += [now_text, "", day_text, ""]
    except Exception as e:
        parts += [f"Цаг агаар авахад алдаа гарлаа: {e}", ""]

    parts.append(get_gold())

    send_telegram("\n".join(parts))
    print("Илгээгдлээ ✅")


if __name__ == "__main__":
    main()