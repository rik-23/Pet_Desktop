"""和主人互动小游戏：猜拳（石头剪刀布）。
点击宠物出拳，宠物随机出，分胜负后给表情反馈。"""
import random
import config
from .base import Action


class GameAction(Action):
    name = "game"

    def __init__(self, pet, duration=4.0):
        super().__init__(pet)
        self.duration = duration
        self.phase = "choose"   # choose -> show -> result
        self.player = None
        self.cpu = None
        self.result = ""

    def on_enter(self):
        self.pet.set_state("game")
        self.pet.app.ui.toast("出拳！石头/剪刀/布（聊天里输入）")
        # 调出聊天让主人选
        self.pet.app.after_chat_game = self._on_choice

    def _on_choice(self, text):
        text = (text or "").strip()
        if text in ("石头", "剪刀", "布", "rock", "scissors", "paper"):
            self.player = {"石头": "rock", "剪刀": "scissors", "布": "paper",
                           "rock": "rock", "scissors": "scissors", "paper": "paper"}[text]
            self.cpu = random.choice(["rock", "scissors", "paper"])
            self.phase = "show"
            self.t = 0.0
            self.result = self._judge()

    def _judge(self):
        p, c = self.player, self.cpu
        if p == c:
            return "平局！再来一局~"
        win = (p == "rock" and c == "scissors") or \
              (p == "scissors" and c == "paper") or \
              (p == "paper" and c == "rock")
        return "你赢啦！🎉" if win else "嘿嘿我赢！"

    def tick(self, dt):
        self.t += dt
        if self.phase == "show" and self.t >= self.duration:
            # 反馈
            if "赢" in self.result and "你" in self.result:
                self.pet.app.ui.say(self.pet, "happy")
            else:
                self.pet.app.ui.say(self.pet, "chatter")
            return True
        if self.phase == "choose" and self.t >= self.duration:
            # 超时没选，取消
            self.pet.app.ui.toast("不玩啦~")
            return True
        return False
