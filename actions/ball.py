"""玩球动作：宠物原地拍球/接球，球上下弹跳。"""
import math
import config
from .base import Action


class BallAction(Action):
    name = "ball"

    def __init__(self, pet, duration=5.0):
        super().__init__(pet)
        self.duration = duration
        self.ball_y = 0.0
        self.ball_dir = 1
        self.bounce_h = 55

    def on_enter(self):
        self.pet.set_state("ball")
        self.pet.app.ui.say(self.pet, "ball")
        self.pet.app.sound.play("notify")

    def tick(self, dt):
        self.t += dt
        # 球上下弹跳（sin 模拟）
        self.ball_y = abs(math.sin(self.t * 4.0)) * self.bounce_h
        if self.pet.app.cfg.get("tts") and self.t < 0.3:
            self.pet.app.sound.speak("接球！")
        if self.t >= self.duration:
            return True
        return False

    def draw(self, canvas, cx, cy):
        # 球画在宠物前下方，随 ball_y 上下
        by = cy + 30 - self.ball_y
        r = 10
        canvas.create_oval(cx - r, by - r, cx + r, by + r,
                          fill=(255, 80, 80, 255), outline=(120, 0, 0, 255))
