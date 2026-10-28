"""行走动作：支持 8 方向（上/下/左/右/四个斜向）+ 镜像朝向。"""
import random
import config
from .base import Action


class WalkAction(Action):
    name = "walk"

    def __init__(self, pet, dx=0, dy=0, duration=None):
        super().__init__(pet)
        # 方向向量（已归一化思路：仅给 8 方向之一）
        self.dx = dx
        self.dy = dy
        # 朝向：dx<0 朝左则镜像
        self.facing = -1 if dx < 0 else 1
        self.duration = duration if duration else random.uniform(1.2, 3.0)
        self.speed = config.WALK_SPEED

    def on_enter(self):
        self.pet.set_state("walk")
        # 朝左镜像
        self.pet.facing = self.facing

    def tick(self, dt):
        self.t += dt
        step = self.speed
        nx = self.pet.x + self.dx * step
        ny = self.pet.y + self.dy * step
        # 边界反弹
        if nx < 0 or nx > self.pet.app.SCREEN_W - config.PET_SIZE:
            self.dx *= -1
            self.facing *= -1
            self.pet.facing = self.facing
            nx = max(0, min(nx, self.pet.app.SCREEN_W - config.PET_SIZE))
        if ny < 0 or ny > self.pet.app.SCREEN_H - config.PET_SIZE:
            self.dy *= -1
            ny = max(0, min(ny, self.pet.app.SCREEN_H - config.PET_SIZE))
        self.pet.x, self.pet.y = nx, ny
        self.pet.sync_pos()
        # 偶尔留脚印
        if random.random() < 0.25:
            self.pet.app.add_footprint(self.pet.x + config.PET_SIZE / 2,
                                       self.pet.y + config.PET_SIZE)
        if self.t >= self.duration:
            return True
        return False
