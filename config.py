"""配置与常量：路径、尺寸、皮肤、台词。"""
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(APP_DIR, "sounds")
SONG_DIR = os.path.join(SOUND_DIR, "songs")
CONFIG_FILE = os.path.join(APP_DIR, "pet_config.json")
BGM_FILE = os.path.join(SOUND_DIR, "bgm.mp3")

PET_SIZE = 100          # 宠物画布尺寸
WIN_PAD = 20            # 根窗口比宠物大多少
WALK_SPEED = 2.2        # 走路速度(px/帧)
BALL_SPEED = 4.0

SKINS = {
    "penguin": {"body": (52, 54, 66), "belly": (255, 255, 255), "beak": (255, 170, 40), "name": "企鹅"},
    "cat":     {"body": (196, 178, 160), "belly": (245, 235, 225), "beak": (40, 40, 40), "name": "猫"},
    "dog":     {"body": (170, 128, 86), "belly": (238, 222, 196), "beak": (40, 40, 40), "name": "狗"},
    "dino":    {"body": (96, 184, 98), "belly": (208, 242, 206), "beak": (40, 40, 40), "name": "恐龙"},
}

TALKS = {
    "idle": ["发呆中…", "在想好吃的", "今天天气不错~", "你也在看我吗？"],
    "chatter": ["你知道吗", "刚才看到一只蝴蝶", "我有点困了", "要不要一起玩"],
    "happy": ["耶！", "好开心~", "最喜欢你了", "嘿嘿"],
    "hide": ["躲好咯~", "来找我呀", "我藏起来啦"],
    "found": ["被找到啦！", "你怎么这么快", "算你厉害"],
    "sing": ["啦啦啦~", "我唱得好听吗", "再来一首！"],
    "ball": ["接球！", "看我的", "传给你~"],
    "pc": ["敲代码中…", "bug 又来了", "马上就好"],
    "hunger": ["我饿啦…", "想吃小鱼干", "喂喂我嘛"],
    "sleep": ["晚安~", "zzz", "好困…"],
    "coquetry": ["人家要抱抱嘛~", "陪我玩嘛", "最喜欢你了♡", "摸摸头~"],
    "angry": ["哼，不理你了！", "你坏！", "我生气了！", "不高兴…"],
}

DEFAULT_CONFIG = {
    "x": 200, "y": 200,
    "skin": "penguin",
    "pets": 1,
    "tts": True,
    "auto_behavior": True,
    "follow": False,
    "bgm": False,
    "hunger": 80,
    "mood": "happy",
}
