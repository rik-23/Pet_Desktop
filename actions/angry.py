"""生气动作：身体抖动 + 怒气符号气泡，表情炸毛。"""
import math
import config
from .base import Action


class AngryAction(Action):
    name = "angry"

    def __init__(self, pet, duration=2.8):
        super().__init__(pet)
        self.duration = duration

    def on_enter(self):
        self.base_x0 = self.pet.x
        self.pet.set_state("angry")
        self.pet.mood = "angry"
        self.pet.app.ui.toast("哼！不理你了！(╯°□°)╯")
        if self.pet.app.cfg.get("tts"):
            self.pet.app.sound.speak("哼，我生气了！")

    def tick(self, dt):
        self.t += dt
        # 高频抖动
        shake = math.sin(self.t * 30.0) * 4
        self.pet.x = self.base_x0 + shake
        self.pet.angle = int(math.sin(self.t * 25.0) * 8)
        self.pet.sync_pos()
        if self.t >= self.duration:
            self.pet.angle = 0
            self.pet.mood = "happy"
            return True
        return False
