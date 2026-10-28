"""奔跑动作：速度约为走路2倍，8方向 + 上下弹跳 + 镜像朝向。"""
import random
import math
import config
from .base import Action


class RunAction(Action):
    name = "run"

    def __init__(self, pet, dx=0, dy=0, duration=None):
        super().__init__(pet)
        self.dx = dx
        self.dy = dy
        self.facing = -1 if dx < 0 else 1
        self.duration = duration if duration else random.uniform(1.0, 2.4)
        self.speed = config.WALK_SPEED * 2.1

    def on_enter(self):
        self.pet.set_state("run")
        self.pet.facing = self.facing

    def tick(self, dt):
        self.t += dt
        step = self.speed
        nx = self.pet.x + self.dx * step
        ny = self.pet.y + self.dy * step
        if nx < 0 or nx > self.pet.app.SCREEN_W - config.PET_SIZE:
            self.dx *= -1
            self.facing *= -1
            self.pet.facing = self.facing
            nx = max(0, min(nx, self.pet.app.SCREEN_W - config.PET_SIZE))
        if ny < 0 or ny > self.pet.app.SCREEN_H - config.PET_SIZE:
            self.dy *= -1
            ny = max(0, min(ny, self.pet.app.SCREEN_H - config.PET_SIZE))
        # 奔跑弹跳
        bounce = abs(math.sin(self.t * 18)) * 6
        self.pet.x, self.pet.y = nx, ny - bounce
        self.pet.sync_pos()
        if random.random() < 0.35:
            self.pet.app.add_footprint(self.pet.x + config.PET_SIZE / 2,
                                       self.pet.y + config.PET_SIZE)
        if self.t >= self.duration:
            return True
        return False
