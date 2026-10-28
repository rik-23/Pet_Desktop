"""撒娇动作：原地小蹦跳 + 爱心气泡，表情软萌。"""
import math
import config
from .base import Action


class CoquetryAction(Action):
    name = "coquetry"

    def __init__(self, pet, duration=3.0):
        super().__init__(pet)
        self.duration = duration
        self.base_y = pet.y

    def on_enter(self):
        self.pet.set_state("coquetry")
        self.pet.mood = "happy"
        # 撒娇台词气泡
        self.pet.app.ui.say(self.pet, "happy")
        if self.pet.app.cfg.get("tts"):
            self.pet.app.sound.speak("人家要抱抱嘛~")

    def tick(self, dt):
        self.t += dt
        # 左右轻晃 + 上下小蹦
        w = math.sin(self.t * 5.0)
        self.pet.facing = -1 if w < 0 else 1
        bounce = abs(math.sin(self.t * 7.0)) * 7
        self.pet.y = self.base_y - bounce
        self.pet.angle = int(w * 6)
        self.pet.sync_pos()
        if self.t >= self.duration:
            self.pet.y = self.base_y
            self.pet.angle = 0
            return True
        return False
