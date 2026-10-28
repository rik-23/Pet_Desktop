"""主应用：窗口、宠物管理、菜单、循环、各种功能。"""
import os
import json
import time
import random
import tkinter as tk

import config
from pet import Pet
from render import make_frame
from sound import SoundManager
from ui import UI
import actions
import diary

try:
    from pynput import mouse as _pynput_mouse
    PYNPUT_OK = True
except Exception:
    PYNPUT_OK = False


class DesktopPetApp:
    def __init__(self):
        self.cfg = self.load_config()
        self.root = tk.Tk()
        self.root.withdraw()
        self.SCREEN_W = self.root.winfo_screenwidth()
        self.SCREEN_H = self.root.winfo_screenheight()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "magenta")
        self.root.configure(bg="magenta")
        WIN = config.PET_SIZE + config.WIN_PAD * 2
        self.root.geometry(f"{WIN}x{WIN}+{self.cfg['x']}+{self.cfg['y']}")
        self.root.deiconify()

        self.sound = SoundManager(self)
        self.ui = UI(self)
        self.songs = self.sound.load_songs()

        self.pets = []
        self.footprints = []
        self._build_footprint_layer()
        self.spawn_pets()

        if PYNPUT_OK:
            try:
                self._ms = _pynput_mouse.Listener(on_click=self._global_on_click)
                self._ms.daemon = True
                self._ms.start()
            except Exception:
                pass

        self.root.bind("<Double-Button-1>", self.on_double_click)
        self.last_tick = time.time()
        # 启动写一条日记（若今天还没写）
        if not diary.today_entries():
            diary.add_entry(self, text="新的一天开始啦，陪在主人身边~")
        self.root.after(120, self.tick)

    # ---------- 配置 ----------
    def load_config(self):
        if os.path.exists(config.CONFIG_FILE):
            try:
                with open(config.CONFIG_FILE, encoding="utf-8") as f:
                    c = json.load(f)
                c.update({k: c.get(k, v) for k, v in config.DEFAULT_CONFIG.items()})
                return c
            except Exception:
                pass
        return dict(config.DEFAULT_CONFIG)

    def save_config(self):
        try:
            with open(config.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ---------- 宠物管理 ----------
    def spawn_pets(self):
        offsets = [(0, 0), (60, 10), (-60, 10)]
        n = self.cfg.get("pets", 1)
        for i in range(max(1, n)):
            pet = Pet(self, i, offsets[i % len(offsets)], persistent=True)
            pet.x = self.cfg["x"] + config.WIN_PAD + offsets[i % len(offsets)][0]
            pet.y = self.cfg["y"] + config.WIN_PAD + offsets[i % len(offsets)][1]
            self.pets.append(pet)

    def add_pet(self, persistent=False):
        idx = len(self.pets)
        offsets = [(0, 0), (60, 10), (-60, 10)]
        p = Pet(self, idx, offsets[idx % len(offsets)], persistent)
        p.x = self.cfg["x"] + config.WIN_PAD + random.randint(-40, 40)
        p.y = self.cfg["y"] + config.WIN_PAD + random.randint(-40, 40)
        self.pets.append(p)
        if not persistent:
            p.expire_at = time.time() + 5
            self.root.after(5000, lambda: self.remove_pet(p))

    def remove_pet(self, pet):
        if pet in self.pets:
            try:
                pet.canvas.destroy()
            except Exception:
                pass
            self.pets.remove(pet)
            offsets = [(0, 0), (60, 10), (-60, 10)]
            for i, p in enumerate(self.pets):
                p.idx = i
                p.offset = offsets[i % len(offsets)]
                p.x = self.cfg["x"] + config.WIN_PAD + p.offset[0]
                p.y = self.cfg["y"] + config.WIN_PAD + p.offset[1]
                p.sync_pos()

    def self_summon(self):
        self.add_pet(persistent=False)

    # ---------- 脚印 ----------
    def _build_footprint_layer(self):
        self.fp_win = tk.Toplevel(self.root)
        self.fp_win.withdraw()
        self.fp_win.overrideredirect(True)
        self.fp_win.attributes("-topmost", True)
        self.fp_win.attributes("-transparentcolor", "magenta")
        self.fp_win.configure(bg="magenta")
        self.fp_win.geometry(f"{self.SCREEN_W}x{self.SCREEN_H}+0+0")
        self.fp_layer = tk.Canvas(self.fp_win, width=self.SCREEN_W, height=self.SCREEN_H,
                                  bg="magenta", highlightthickness=0)
        self.fp_layer.pack()
        self.fp_win.deiconify()

    def add_footprint(self, x, y):
        self.footprints.append([x, y, 120])
        if len(self.footprints) > 40:
            self.footprints.pop(0)

    def draw_footprints(self):
        self.fp_layer.delete("all")
        for fp in self.footprints:
            alpha = max(0, fp[2])
            color = f"#{int(alpha):02x}{int(alpha):02x}{int(alpha):02x}"
            self.fp_layer.create_oval(fp[0] - 3, fp[1] - 3, fp[0] + 3, fp[1] + 3,
                                     fill=color, outline="")

    # ---------- 全局点击找它 ----------
    def _global_on_click(self, x, y, button, pressed):
        if pressed and button == _pynput_mouse.Button.left:
            now = time.time()
            if now - getattr(self, "_last_click_t", 0) < 0.35:
                self.root.after(0, self._reveal_all_hidden)
            self._last_click_t = now

    def _reveal_all_hidden(self):
        found = any(p.hidden for p in self.pets)
        for p in self.pets:
            if p.hidden:
                p.reveal(found=True)
        if not found:
            self.root.attributes("-topmost", True)

    def on_double_click(self, e):
        found = any(p.hidden for p in self.pets)
        for p in self.pets:
            if p.hidden:
                p.reveal(found=True)
        if not found:
            self.ui.toast("我没躲哦~ 点我可以聊天 💬")

    # ---------- 歌词搜索 ----------
    def search_lyrics(self):
        self.lyric_error = None
        try:
            import requests
        except Exception:
            self.lyric_error = "未联网(requests不可用)"
            return None
        try:
            r = requests.get("https://v1.hitokoto.cn/", timeout=6,
                             headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            data = r.json()
            text = data.get("hitokoto", "").strip()
            if text:
                title = data.get("from") or "随机一句"
                lines = [text[i:i + 12] for i in range(0, len(text), 12)] or [text]
                return title, lines
        except Exception as e:
            self.lyric_error = f"hitokoto失败：{type(e).__name__} {e}"
        try:
            import re
            kw = random.choice(["儿歌", "流行歌", "民谣", "童谣", "轻音乐"])
            r2 = requests.get(f"https://www.baidu.com/s?wd={kw}歌词", timeout=6,
                              headers={"User-Agent": "Mozilla/5.0"})
            r2.raise_for_status()
            lines = re.findall(r"[一-龥]{4,20}[，。！？、]", r2.text)
            lines = [l.strip() for l in lines if len(l) >= 5][:6]
            if lines:
                return random.choice(["搜到的歌", kw + "精选", "随机一首"]), lines
            self.lyric_error = "搜到页面但没提取到歌词，改用本地歌"
            return None
        except Exception as e:
            self.lyric_error = f"搜索异常：{type(e).__name__} {e}"
            return None

    # ---------- 唱歌（上网搜歌词 + 语音朗读，不播本地） ----------
    def start_sing(self, pet):
        pet.start_action("sing")
        pet.busy_until = time.time() + random.randint(15, 22)
        self.ui.say(pet, "sing")
        try:
            lyric = self.search_lyrics()
            if lyric:
                title, lines = lyric
                self.ui.show_lyric(pet, title, lines)
                if self.cfg.get("tts"):
                    self.sound.speak(f"我来唱一首{title}：" + " ".join(lines))
                else:
                    self.ui.toast(f"搜到《{title}》歌词，开语音播报就能唱🎤")
                diary.add_entry(self, text=f"我上网学了一首歌《{title}》，唱给你听~", mood="开心")
            else:
                reason = getattr(self, "lyric_error", "未知原因")
                self.ui.toast(f"没搜到歌词（{reason}），我用内置的哼两句~")
                if self.cfg.get("tts"):
                    self.sound.speak(random.choice(config.TALKS["sing"]))
                diary.add_entry(self, text="想唱歌但没搜到歌词，哼了段内置的。", mood="平静")
        except Exception as e:
            print(f"[唱歌异常] {type(e).__name__}: {e}")
            self.ui.toast("唱歌出错了，但我在~ 再点一次试试")
        self.sound.play("talk")
        pet.busy_done()

    # ---------- 听歌（播放本地音乐） ----------
    def start_listen(self, pet=None):
        pet = pet or self.pets[0]
        if not self.songs:
            self.ui.toast("sounds/songs/ 里还没有歌~ 放一首进去就能听")
            diary.add_entry(self, text="想听歌但没有本地音乐文件。", mood="平静")
            return
        ok, name = self.sound.play_song(self)
        if ok:
            self.ui.toast(f"我在听歌：{name}🎶")
            diary.add_entry(self, text=f"我放了一首本地歌《{name}》~", mood="开心")
        else:
            self.ui.toast("本地歌播放失败了…")

    # ---------- 聊天 ----------
    def chat_with(self, pet):
        dlg = self.ui.ask("聊天", "对我说点什么（输入'唱xxx'点歌 / '石头 剪刀 布'猜拳）：")
        text = dlg.result
        if not text:
            return
        if text.startswith("唱"):
            self.start_sing(pet)
            return
        # 猜拳游戏回调
        cb = getattr(self, "after_chat_game", None)
        if cb is not None:
            cb(text)
            self.after_chat_game = None
            return
        self.ui.toast(f"你：{text}")
        self.ui.say(pet, "chatter")

    # ---------- 菜单 ----------
    def build_menu(self, pet=None):
        self.menu = tk.Menu(self.root, tearoff=0)
        p = pet or self.pets[0]
        self.menu.add_command(label="💬 聊天", command=lambda: self.chat_with(p))
        self.menu.add_command(label="🎵 唱歌", command=lambda: self.start_sing(p))
        self.menu.add_command(label="🎶 听歌", command=lambda: self.sound.play_song(self))
        self.menu.add_command(label="🚶 走路", command=lambda: p.start_action("walk", 1, 0))
        self.menu.add_command(label="🏃 奔跑", command=lambda: p.start_action("run", 1, 0))
        self.menu.add_command(label="🤸 翻跟头", command=lambda: p.start_action("roll"))
        self.menu.add_command(label="💃 跳舞", command=lambda: p.start_action("dance"))
        self.menu.add_command(label="💕 撒娇", command=lambda: p.start_action("coquetry"))
        self.menu.add_command(label="😡 生气", command=lambda: p.start_action("angry"))
        self.menu.add_command(label="🏀 玩球", command=lambda: p.start_action("ball"))
        self.menu.add_command(label="🎮 玩游戏(猜拳)", command=lambda: p.start_action("game"))
        self.menu.add_separator()
        self.menu.add_command(label="🐧 召唤同伴", command=self.self_summon)
        self.menu.add_command(label="👻 躲起来", command=p.start_hide)
        self.menu.add_command(label="⏹ 停止动作", command=self.stop_busy)
        self.menu.add_command(label="🍪 喂食", command=lambda: self.feed(p))
        self.menu.add_command(label="👋 戳一下", command=lambda: self.poke(p))
        self.menu.add_command(label="😴 睡觉", command=self.toggle_sleep)
        self.menu.add_separator()
        self.menu.add_command(label="⚙ 设置", command=self.ui.settings_window)
        self.menu.add_command(label="📔 看日记", command=self.show_diary)
        self.menu.add_command(label="🎨 换皮肤", command=self.change_skin)
        self.menu.add_command(label="🚪 退出", command=self.quit_app)
        try:
            self.menu.tk_popup(self.root.winfo_x() + config.PET_SIZE // 2,
                               self.root.winfo_y() + config.PET_SIZE)
        except Exception:
            pass

    def stop_busy(self):
        for p in self.pets:
            if p.busy:
                p.busy_done()
                p.set_state("idle")
        self.ui.toast("好哒，不动了~")

    def feed(self, pet=None):
        pet = pet or self.pets[0]
        self.cfg["hunger"] = min(100, self.cfg.get("hunger", 80) + 20)
        self.ui.say(pet, "happy")
        self.sound.play("talk")
        diary.add_entry(self, text="主人喂我了，好幸福~", mood="开心")

    def poke(self, pet=None):
        pet = pet or self.pets[0]
        self.ui.say(pet, "chatter")
        self.sound.play("notify")
        diary.add_entry(self, text="主人戳了我一下，痒痒的。", mood="撒娇中")

    def toggle_sleep(self):
        p = self.pets[0]
        if p.state == "sleep":
            p.set_state("idle")
        else:
            p.set_state("sleep")

    def show_diary(self):
        entries = diary.recent_entries(15)
        text = diary.format_entries(entries)
        top = tk.Toplevel(self.root)
        top.title("企鹅日记 📔")
        top.attributes("-topmost", True)
        txt = tk.Text(top, width=46, height=18, font=("Microsoft YaHei", 10), wrap="word")
        txt.insert("1.0", text)
        txt.config(state="disabled")
        txt.pack(padx=10, pady=10)
        tk.Button(top, text="关闭", command=top.destroy).pack(pady=5)

    def change_skin(self):
        names = list(config.SKINS.keys())
        cur = names.index(self.cfg.get("skin", "penguin"))
        self.cfg["skin"] = names[(cur + 1) % len(names)]
        self.save_config()
        self.ui.toast(f"皮肤切换为：{config.SKINS[self.cfg['skin']]['name']}")

    def quit_app(self):
        self.save_config()
        try:
            self.root.destroy()
        except Exception:
            pass

    # ---------- 主循环 ----------
    def tick(self):
        now = time.time()
        dt = min(0.1, now - self.last_tick)
        self.last_tick = now
        for p in list(self.pets):
            p.tick(dt)
        for p in self.pets:
            p.draw()
        # 脚印淡出
        for fp in self.footprints:
            fp[2] -= dt * 60
        self.footprints = [f for f in self.footprints if f[2] > 0]
        self.draw_footprints()
        # 游戏动作结束清理
        if getattr(self, "after_chat_game", None) is not None and not any(
                p.current_action and p.current_action.name == "game" for p in self.pets):
            self.after_chat_game = None

        # 空闲碎碎念（自主触发，不需点击）：每隔随机 6~12 秒来一句
        p0 = self.pets[0]
        if not hasattr(self, "next_chat_t"):
            self.next_chat_t = now + random.uniform(6, 12)
        if (self.cfg.get("tts") and self.cfg.get("auto_behavior")
                and not p0.hidden
                and (p0.current_action is None or p0.current_action.name != "game")
                and now >= self.next_chat_t):
            kind = random.choice(["idle", "chatter", "happy", "coquetry"])
            self.ui.say(p0, kind)
            self.next_chat_t = now + random.uniform(6, 12)
        self.root.after(120, self.tick)

    def run(self):
        # 不再自动播放 BGM
        self.root.mainloop()


def run():
    """程序入口。"""
    app = DesktopPetApp()
    app.run()
