"""
components/greeting.py
来訪回数・天気に応じた「気の利いた一言」生成モジュール
将来的にAI生成へ置き換えやすいよう、関数として分離している
"""

BAD_WEATHER = {"Rain", "Drizzle", "Thunderstorm", "Snow"}


def generate_greeting_message(visit_count: int, weather: dict) -> str:
    """
    来訪回数・天気に応じた、気の利いた一言を生成する。
    visit_count: 来訪回数（1回目から）
    weather: {"emoji": ..., "text": ..., "main": ...} 形式の辞書
    """
    main = weather.get("main", "")
    text = weather.get("text", "")

    if visit_count <= 1:
        # 初回はシンプルな挨拶のみ（天気の話はしない）
        return "ようこそお越しくださいました。"

    # 2回目以降：天気が悪い場合は気遣いの一言を追加
    if main in BAD_WEATHER and text:
        return f"お待ちしておりました。本日は{text}の中ご来社いただきありがとうございます。"

    # 天気が良い場合は天気の話をせず、シンプルな再来訪の挨拶のみ
    return "お待ちしておりました。"
