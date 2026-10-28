"""动作基类：所有动作的接口约定。"""


class Action:
    """宠物动作基类。

    pet: 持有该动作的 Pet 实例。
    实现 tick(dt) 推进动画，返回 True 表示动作结束（回到 idle）。
    """

    name = "idle"

    def __init__(self, pet):
        self.pet = pet
        self.t = 0.0

    def on_enter(self):
        """进入动作时调用。"""
        pass

    def tick(self, dt):
        """推进一帧，dt 为秒。返回 True 表示结束。"""
        return True

    def draw(self, canvas, cx, cy):
        """在画布上绘制附加效果（可选）。"""
        pass
