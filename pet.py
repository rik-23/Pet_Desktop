"""宠物实体：状态、绘制、交互、动作调度。"""
import tkinter as tk
from PIL import Image, ImageTk
import config
import actions
import diary
from render import load_or_make, rotate_image, draw_shadow


def tint(img, color):
    """将图像整体染上指定色调（用于生气变红）。"""
    r, g, b = color
    out = img.copy()
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            pr, pg, pb, pa = px[x, y]
            if pa > 0:
                nr = (pr + r) // 2
                ng = (pg + g) // 2
                nb = (pb + b) // 2
                px[x, y] = (nr, ng, nb, pa)
    return out


 
# 动作 -> 日记文案（记录它干了什么）
ACTION_DIARY = {
    "walk": ("walk", "溜达了一会儿~"),
    "run": ("run", "跑得飞快，像一阵风！"),
    "roll": ("roll", "翻了个跟头，超帅的。"),
    "dance": ("dance", "跳了支舞，扭扭扭~"),
    "coquetry": ("coquetry", "向主人撒了个娇♡"),
    "angry": ("angry", "有点小生气，哼。"),
    "ball": ("ball", "拍了会儿球。"),
}
class Pet:
    def __init__(self, app, idx=0, offset=(0, 0), persistent=False):
        self.app = app
        self.idx = idx
        self.offset = offset
        self.persistent = persistent

        self.state = "idle"
        self.mood = app.cfg.get("mood", "happy")
        self.x = app.cfg["x"] + offset[0]
        self.y = app.cfg["y"] + offset[1]
        self.hidden = False
        self.hide_until = 0
        self.busy = False
        self.busy_type = None
        self.busy_until = 0
        self.expire_at = 0

        self.facing = 1           # 1 右, -1 左
        self.angle = 0            # 旋转角度（翻跟头/跳舞用）
        self.frame_idx = 0
        self.anim_t = 0.0
        self._dragging = False
        self._imgtk = None

        self.current_action = None
        self.idle_t = 0.0

        # 画布
        self.canvas = tk.Canvas(app.root, width=config.PET_SIZE, height=config.PET_SIZE,
                                bg="magenta", highlightthickness=0)
        self.canvas.place(x=config.WIN_PAD, y=config.WIN_PAD)
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.show_menu)
        self.canvas.bind("<Double-Button-1>", lambda e: self.app.on_double_click(e))
        self.sync_pos()

    # ---------- 位置 ----------
    def sync_pos(self):
        self.x = max(0, min(self.x, self.app.SCREEN_W - config.PET_SIZE))
        self.y = max(0, min(self.y, self.app.SCREEN_H - config.PET_SIZE))
        base_x = int(self.x - config.WIN_PAD)
        base_y = int(self.y - config.WIN_PAD)
        self.app.cfg["x"], self.app.cfg["y"] = base_x, base_y
        self.app.root.geometry(f"+{base_x}+{base_y}")
        self.canvas.place(x=config.WIN_PAD, y=config.WIN_PAD)

    def get_center(self):
        return (self.x + config.PET_SIZE / 2, self.y + config.PET_SIZE / 2)

    # ---------- 状态 ----------
    def set_state(self, st):
        self.state = st
        self.frame_idx = 0

    def set_hidden(self, v):
        self.hidden = v


    # ---------- 动作调度 ----------

    def start_action(self, name, *args, **kwargs):
        act = actions.get_action(name, self, *args, **kwargs)
        if act is None:
            return
        self.current_action = act
        act.on_enter()
        self.busy = True
        self.busy_type = name
        self.busy_until = 0
        # 写一句日记：记录它干了什么
        if name in ACTION_DIARY:
            _, text = ACTION_DIARY[name]
            try:
                diary.add_entry(self.app, text=text, mood="平静")
            except Exception:
                pass

    def busy_done(self):
        self.current_action = None
        self.busy = False
        self.busy_type = None
        self.set_state("idle")

    # ---------- 交互 ----------
    def on_press(self, e):
        self._drag_offset = (e.x, e.y)
        self._dragging = False

    def on_drag_move(self, e):
        if self.hidden:
            return
        self._dragging = True
        nx = max(0, min(self.app.root.winfo_x() + (e.x - self._drag_offset[0]),
                        self.app.SCREEN_W - config.PET_SIZE))
        ny = max(0, min(self.app.root.winfo_y() + (e.y - self._drag_offset[1]),
                        self.app.SCREEN_H - config.PET_SIZE))
        self.app.cfg["x"], self.app.cfg["y"] = nx, ny
        self.app.root.geometry(f"+{nx}+{ny}")
        for p in self.app.pets:
            p.x = nx + p.offset[0]
            p.y = ny + p.offset[1]
            p.sync_pos()

    def on_release(self, e):
        if self._dragging:
            self._dragging = False
            self.app.save_config()
            return
        if self.hidden:
            self.reveal(found=True)
            return
        self.app.chat_with(self)

    def show_menu(self, e):
        self.app.build_menu(self)

    def reveal(self, found=True):
        self.set_hidden(False)
        if found:
            self.app.ui.say(self, "found")
            self.app.sound.play("talk")

    def start_hide(self):
        import random
        spots = [(200, 200), (600, 300), (300, 500), (800, 150)]
        nx, ny = random.choice(spots)
        self.app.cfg["x"], self.app.cfg["y"] = nx, ny
        self.x, self.y = nx, ny
        self.hide_until = __import__("time").time() + random.randint(8, 15)
        self.set_hidden(True)
        self.app.ui.say(self, "hide")
        self.app.sound.play("talk")
        self.sync_pos()

    # ---------- 每帧 ----------
    def tick(self, dt):
        import random
        now = __import__("time").time()
        if self.hidden:
            if now >= self.hide_until:
                self.reveal(found=False)
            return
        if self.expire_at and now >= self.expire_at:
            self.app.remove_pet(self)
            return
        # 动作推进
        if self.current_action is not None:
            ended = self.current_action.tick(dt)
            if ended:
                self.busy_done()
            return
        # 空闲：自主小动作（全自主，不点也会发生）

        if self.idle_t > 1.5 and self.app.cfg.get("auto_behavior"):
            self.idle_t = 0.0
            if random.random() < 0.6:
                choice = random.choice(actions.RANDOM_ACTIONS)
                if choice in ("walk", "run"):
                    dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1),
                                            (1, 1), (1, -1), (-1, 1), (-1, -1)])
                    self.start_action(choice, dx, dy)
                else:
                    self.start_action(choice)
            else:
                self.idle_t += dt
                last = getattr(self.app, "last_music_t", 0.0)
                if now - last > random.uniform(90, 240):  # 距上次 1.5~4 分钟内最多一次
                    self.app.last_music_t = now
                    # 50% 听本地歌 / 50% 上网唱歌

    def draw(self):
        self.canvas.delete("all")
        if self.hidden:
            draw_shadow(self.canvas, 40, 45, 80, 85)
            return
        skin = self.app.cfg.get("skin", "penguin")
        state = self.state if self.state in ("walk", "run", "roll", "dance",
                                             "coquetry", "angry", "ball", "game", "sleep") else "idle"
        img = load_or_make(state, skin, self.frame_idx, config.PET_SIZE)
        if self.state == "angry":
            img = tint(img, (255, 120, 120))
        if self.angle:
            img = rotate_image(img, self.angle)
        if self.facing < 0:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        self._imgtk = ImageTk.PhotoImage(img)
        self.canvas.create_image(config.PET_SIZE // 2, config.PET_SIZE // 2,
                                 image=self._imgtk)
        # 动作附加绘制（如玩球的球）
        if self.current_action is not None and hasattr(self.current_action, "draw"):
            try:
                self.current_action.draw(self.canvas, config.PET_SIZE // 2, config.PET_SIZE // 2)
            except Exception:
                pass
        # 动画帧推进
        self.anim_t += 1
        if self.state in ("walk", "run") and self.anim_t % 6 == 0:
            self.frame_idx = (self.frame_idx + 1) % 4
        elif self.state in ("idle", "dance", "roll", "coquetry", "angry", "ball", "game") and self.anim_t % 12 == 0:
            self.frame_idx = (self.frame_idx + 1) % 2