"""动作注册表：集中管理所有可调用动作。"""
from .base import Action
from .walk import WalkAction
from .run import RunAction
from .roll import RollAction
from .dance import DanceAction
from .coquetry import CoquetryAction
from .angry import AngryAction
from .ball import BallAction
from .game import GameAction

# 动作名 -> 类
ACTION_REGISTRY = {
    "walk": WalkAction,
    "run": RunAction,
    "roll": RollAction,
    "dance": DanceAction,
    "coquetry": CoquetryAction,
    "angry": AngryAction,
    "ball": BallAction,
    "game": GameAction,
}

# 自主行为可随机触发的动作（全自主，不点也会发生）
RANDOM_ACTIONS = ["walk", "run", "roll", "dance", "coquetry", "angry", "ball"]


def get_action(name, pet, *args, **kwargs):
    cls = ACTION_REGISTRY.get(name)
    if not cls:
        return None
    return cls(pet, *args, **kwargs)
