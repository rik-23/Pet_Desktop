"""跳舞动作：左右摇摆 + 上下蹦跳 + 偶尔转圈。"""
import math
import config
from .base import Action


class DanceAction(Action):
    name = "dance"

    def __init__(self, pet, duration=4.0):
        super().__init__(pet)
        self.duration = duration
        self.base_y = pet.y

    def on_enter(self):
        self.pet.set_state("dance")

    def tick(self, dt):
        self.t += dt
        # 左右摇摆（facing 翻转模拟）
        w = math.sin(self.t * 6.0)
        self.pet.facing = -1 if w < 0 else 1
        self.pet.angle = int(w * 12)  # 轻微倾斜
        # 上下蹦跳
        bounce = abs(math.sin(self.t * 8.0)) * 8
        self.pet.y = self.base_y - bounce
        self.pet.sync_pos()
        if self.t >= self.duration:
            self.pet.y = self.base_y
            self.pet.angle = 0
            return True
        return False
