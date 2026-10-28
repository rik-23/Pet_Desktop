"""翻跟头动作：原地做 360° 翻转（用 rotate 角度绘制）。"""
import config
from .base import Action


class RollAction(Action):
    name = "roll"

    def __init__(self, pet, times=1):
        super().__init__(pet)
        self.times = times
        self.total_angle = 360 * times
        self.duration = 0.9 * times

    def on_enter(self):
        self.pet.set_state("roll")
        self.pet.angle = 0

    def tick(self, dt):
        self.t += dt
        progress = min(1.0, self.t / self.duration)
        self.pet.angle = int(self.total_angle * progress)
        if progress >= 1.0:
            self.pet.angle = 0
            return True
        return False
