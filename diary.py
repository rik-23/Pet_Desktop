"""日记：宠物每天自己记录心情与发生的事，可查看。"""
import os
import json
import time
import random
import config

DIARY_FILE = os.path.join(config.APP_DIR, "pet_diary.json")

MOODS = ["开心", "平静", "有点困", "想吃零食", "想玩", "小小生气", "撒娇中"]

TEMPLATES = [
    "今天在主人的桌面上溜达了好久~",
    "偷偷躲起来又被找到了，呜。",
    "主人戳了我一下，好痒！",
    "听到一首好听的歌，跟着哼了半天。",
    "翻了个跟头，感觉自己超厉害。",
    "和主人玩了猜拳，我赢啦（才怪）。",
    "天气不错，想出去走走。",
    "吃了小鱼干，满足！",
    "跳了支舞，主人看见了没？",
    "发了会儿呆，思考企鹅的哲学。",
]


def load_diary():
    if os.path.exists(DIARY_FILE):
        try:
            with open(DIARY_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_diary(entries):
    try:
        with open(DIARY_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def add_entry(app, text=None, mood=None):
    """写一条日记（自动带日期/时间）。"""
    entries = load_diary()
    date = time.strftime("%Y-%m-%d")
    clock = time.strftime("%H:%M")
    if text is None:
        text = random.choice(TEMPLATES)
    if mood is None:
        mood = random.choice(MOODS)
    entries.append({"date": date, "time": clock, "mood": mood, "text": text})
    # 最多保留 200 条
    if len(entries) > 200:
        entries = entries[-200:]
    save_diary(entries)
    return entries[-1]


def today_entries():
    today = time.strftime("%Y-%m-%d")
    return [e for e in load_diary() if e.get("date") == today]


def recent_entries(n=10):
    return load_diary()[-n:]


def format_entries(entries):
    if not entries:
        return "（还没有日记哦~）"
    lines = []
    for e in entries:
        lines.append(f"【{e['date']} {e['time']}】{e['mood']}：{e['text']}")
    return "\n".join(lines)
