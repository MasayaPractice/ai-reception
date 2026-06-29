"""
components/weather.py
天気情報取得モジュール（OpenWeatherMap API使用）
"""
import os
import requests
import streamlit as st

CITY = "Tokyo"

WEATHER_EMOJI = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "☔",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
}

WEATHER_TEXT_JA = {
    "Clear": "晴れ",
    "Clouds": "曇り",
    "Rain": "雨",
    "Drizzle": "小雨",
    "Thunderstorm": "雷雨",
    "Snow": "雪",
    "Mist": "霧",
    "Fog": "霧",
}


def get_weather() -> dict:
    """現在の天気情報を取得する（絵文字・日本語テキスト・気温付き）"""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY") or st.secrets.get("OPENWEATHER_API_KEY", "")
        if not api_key:
            return {"emoji": "", "text": "", "main": "", "temp": 0}

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": CITY, "appid": api_key, "units": "metric", "lang": "ja"}
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()

        main = data.get("weather", [{}])[0].get("main", "")
        emoji = WEATHER_EMOJI.get(main, "")
        text = WEATHER_TEXT_JA.get(main, "")
        temp = round(data.get("main", {}).get("temp", 0))

        return {"emoji": emoji, "text": text, "main": main, "temp": temp}
    except Exception as e:
        print(f"[Weather] 取得エラー: {e}")
        return {"emoji": "", "text": "", "main": "", "temp": 0}
