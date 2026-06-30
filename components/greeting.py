"""
components/greeting.py
来訪回数・天気・曜日・時間帯に応じた「気の利いた一言」生成モジュール
複数テンプレートをランダムに選択して毎回異なる表現を実現
"""
import random
from datetime import datetime

BAD_WEATHER = {"Rain", "Drizzle", "Thunderstorm", "Snow"}

def get_day_of_week() -> str:
    """曜日を返す（日本語）"""
    days = ["月", "火", "水", "木", "金", "土", "日"]
    return days[datetime.now().weekday()]

def get_time_period() -> str:
    """時間帯を返す"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "朝"
    elif 12 <= hour < 17:
        return "昼"
    elif 17 <= hour < 21:
        return "夕方"
    else:
        return "夜"

def generate_greeting_message(visitor_name: str, visit_count: int, weather: dict) -> str:
    """
    訪問者名・来訪回数・天気・曜日・時間帯に応じた「気の利いた一言」を生成
    
    Args:
        visitor_name: 訪問者の名前（例："清遠将也"）
        visit_count: 来訪回数（1, 2, 3, ...）
        weather: {"emoji": "☀️", "text": "晴れ", "main": "Clear", "temp": 23}
    """
    
    # 初回訪問
    if visit_count <= 1:
        return "ようこそお越しくださいました。本日はご利用ありがとうございます。"
    
    # 以降は複数回訪問
    day_of_week = get_day_of_week()
    time_period = get_time_period()
    weather_main = weather.get("main", "")
    weather_text = weather.get("text", "晴れ")
    
    # ========== 優先度2：複合条件（最も具体的） ==========
    
    # 【月曜日 + 朝 + 悪天候】
    if day_of_week == "月" and time_period == "朝" and weather_main in BAD_WEATHER:
        templates = [
            f"{visitor_name}様おはようございます。月曜日の朝、{weather_text}の中のご来社、本当にありがとうございます。",
            f"{visitor_name}様月曜日の朝から{weather_text}、大変な中のご来社ありがとうございます。",
        ]
        return random.choice(templates)
    
    # 【金曜日 + 悪天候】
    if day_of_week == "金" and weather_main in BAD_WEATHER:
        templates = [
            f"{visitor_name}様お待ちしておりました。金曜日の{weather_text}、ご苦労様です。",
            f"{visitor_name}様週末前の{weather_text}、大変ですね。いつもありがとうございます。",
        ]
        return random.choice(templates)
    
    # ========== 優先度3：曜日 + 時間帯 ==========
    
    # 【月曜日 + 朝】
    if day_of_week == "月" and time_period == "朝":
        templates = [
            f"{visitor_name}様おはようございます。月曜日からお疲れ様です。",
            f"{visitor_name}様朝早くからのご来社、本当にありがとうございます。",
            f"{visitor_name}様おはようございます。月曜日は特に大変ですね、お疲れ様です。",
        ]
        return random.choice(templates)
    
    # 【月曜日 + 昼】
    if day_of_week == "月" and time_period == "昼":
        templates = [
            f"{visitor_name}様お待ちしておりました。月曜日もお疲れ様です。",
            f"{visitor_name}様いつもお世話になっております。月曜日のご来社、ありがとうございます。",
        ]
        return random.choice(templates)
    
    # 【金曜日 + 朝】
    if day_of_week == "金" and time_period == "朝":
        templates = [
            f"{visitor_name}様おはようございます。金曜日の朝、本日もよろしくお願いいたします。",
            f"{visitor_name}様朝早くからのご来社、ありがとうございます。",
        ]
        return random.choice(templates)
    
    # 【金曜日 + 昼】
    if day_of_week == "金" and time_period == "昼":
        templates = [
            f"{visitor_name}様お待ちしておりました。金曜日ですね、本日もよろしくお願いいたします。",
            f"{visitor_name}様こんにちは。金曜日も頑張りましょう。",
            f"{visitor_name}様お世話になっております。金曜日の午後、本日もご利用ありがとうございます。",
        ]
        return random.choice(templates)
    
    # ========== 優先度4：曜日のみ ==========
    
    # 【月曜日】
    if day_of_week == "月":
        templates = [
            f"{visitor_name}様お待ちしておりました。月曜日のご来社、いつもありがとうございます。",
            f"{visitor_name}様月曜日もお疲れ様です。本日もよろしくお願いいたします。",
        ]
        return random.choice(templates)
    
    # 【金曜日】
    if day_of_week == "金":
        templates = [
            f"{visitor_name}様お待ちしておりました。金曜日ですね。",
            f"{visitor_name}様こんにちは。金曜日、本日もよろしくお願いいたします。",
            f"{visitor_name}様いつもお世話になっております。",
        ]
        return random.choice(templates)
    
    # 【土曜日・日曜日】
    if day_of_week in ["土", "日"]:
        templates = [
            f"{visitor_name}様お待ちしておりました。週末のご来社、ありがとうございます。",
            f"{visitor_name}様こんにちは。本日もご利用ありがとうございます。",
        ]
        return random.choice(templates)
    
    # ========== 優先度5：天気のみ ==========
    
    # 【雨・雷・雪など悪天候】
    if weather_main in BAD_WEATHER:
        templates = [
            f"{visitor_name}様お待ちしておりました。本日は{weather_text}の中ご来社いただきありがとうございます。",
            f"{visitor_name}様いつもお世話になっております。{weather_text}の中のご来社、ご苦労様です。",
            f"{visitor_name}様こんにちは。{weather_text}ですが、いつもご利用ありがとうございます。",
            f"{visitor_name}様{weather_text}の中、来てくださってありがとうございます。",
        ]
        return random.choice(templates)
    
    # ========== 優先度6：時間帯のみ ==========
    
    # 【朝】
    if time_period == "朝":
        templates = [
            f"{visitor_name}様おはようございます。本日もよろしくお願いいたします。",
            f"{visitor_name}様朝早くからのご来社、ありがとうございます。",
            f"{visitor_name}様おはようございます。いつもお世話になっております。",
        ]
        return random.choice(templates)
    
    # 【昼】
    if time_period == "昼":
        templates = [
            f"{visitor_name}様こんにちは。本日もご利用ありがとうございます。",
            f"{visitor_name}様お待ちしておりました。",
        ]
        return random.choice(templates)
    
    # 【夕方】
    if time_period == "夕方":
        templates = [
            f"{visitor_name}様こんばんは。本日もお疲れ様です。",
            f"{visitor_name}様お待ちしておりました。",
        ]
        return random.choice(templates)
    
    # ========== 優先度7：デフォルト（複数回訪問） ==========
    
    templates = [
        f"{visitor_name}様お待ちしておりました。いつもお世話になっております。",
        f"{visitor_name}様こんにちは。本日もご利用ありがとうございます。",
        f"{visitor_name}様いつもお世話になっております。",
        f"{visitor_name}様本日もよろしくお願いいたします。",
        f"{visitor_name}様お待ちしておりました。",
    ]
    return random.choice(templates)
