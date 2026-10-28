"""UI 层：气泡、歌词气泡、toast、对话框、右键菜单、设置窗口。"""
import tkinter as tk
import config


class UI:
    def __init__(self, app):
        self.app = app
        self.root = app.root

    def say(self, pet, kind):
        text = random_line(kind)
        b = tk.Toplevel(self.root)
        b.overrideredirect(True)
        b.attributes("-topmost", True)
        b.attributes("-transparentcolor", "magenta")
        b.configure(bg="magenta")
        lbl = tk.Label(b, text=text, bg="#fff8dc", fg="#333", font=("Microsoft YaHei", 11),
                       padx=8, pady=4, relief="ridge", bd=2)
        lbl.pack()
        x = pet.x + 10
        y = pet.y - 40
        b.geometry(f"+{int(x)}+{int(y)}")
        self.root.after(2200, lambda: b.destroy())
        if self.app.cfg.get("tts"):
            self.app.sound.speak(text)

    def show_lyric(self, pet, title, lines):
        b = tk.Toplevel(self.root)
        b.overrideredirect(True)
        b.attributes("-topmost", True)
        b.attributes("-transparentcolor", "magenta")
        b.configure(bg="magenta")
        txt = f"♪ {title}\n" + "\n".join(lines[:4])
        lbl = tk.Label(b, text=txt, bg="#e6f0ff", fg="#222", font=("Microsoft YaHei", 10),
                       justify="left", padx=8, pady=5, relief="ridge", bd=2)
        lbl.pack()
        b.geometry(f"+{int(pet.x)+10}+{int(pet.y)-60}")
        self.root.after(5000, lambda: b.destroy())

    def toast(self, text):
        b = tk.Toplevel(self.root)
        b.overrideredirect(True)
        b.attributes("-topmost", True)
        b.attributes("-transparentcolor", "magenta")
        b.configure(bg="magenta")
        lbl = tk.Label(b, text=text, bg="#333", fg="#fff", font=("Microsoft YaHei", 10),
                       padx=8, pady=4)
        lbl.pack()
        b.geometry(f"+{int(self.app.SCREEN_W//2-100)}+{int(self.app.SCREEN_H-80)}")
        self.root.after(2600, lambda: b.destroy())

    def ask(self, title, prompt):
        return InputDialog(self.root, title, prompt)

    def settings_window(self):
        """设置窗口：把常用开关收进一个下拉式面板。"""
        w = tk.Toplevel(self.root)
        w.title("桌宠设置")
        w.attributes("-topmost", True)
        w.configure(bg="#f5f5f5")
        opts = [
            ("语音播报", "tts"),
            ("自主行为(自己动)", "auto_behavior"),
            ("跟随鼠标", "follow"),
            ("背景音乐", "bgm"),
        ]
        vars = {}
        for i, (label, key) in enumerate(opts):
            var = tk.BooleanVar(value=bool(self.app.cfg.get(key, False)))
            vars[key] = var
            tk.Checkbutton(w, text=label, variable=var, bg="#f5f5f5",
                           font=("Microsoft YaHei", 11), anchor="w").grid(
                row=i, column=0, sticky="w", padx=12, pady=6)

        # 皮肤下拉
        tk.Label(w, text="皮肤：", bg="#f5f5f5", font=("Microsoft YaHei", 11)).grid(
            row=len(opts), column=0, sticky="w", padx=12, pady=6)
        skin_names = {v["name"]: k for k, v in config.SKINS.items()}
        skin_var = tk.StringVar(value=config.SKINS[self.app.cfg.get("skin", "penguin")]["name"])
        om = tk.OptionMenu(w, skin_var, *skin_names.keys())
        om.grid(row=len(opts), column=1, padx=8, pady=6)

        def _save():
            for key, var in vars.items():
                self.app.cfg[key] = var.get()
            self.app.cfg["skin"] = skin_names[skin_var.get()]
            self.app.save_config()
            self.toast("设置已保存 ✅")
            w.destroy()

        tk.Button(w, text="保存", command=_save, bg="#4caf50", fg="white",
                  font=("Microsoft YaHei", 11), width=12).grid(
            row=len(opts) + 1, column=0, columnspan=2, pady=10)


class InputDialog:
    def __init__(self, parent, title, prompt):
        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.attributes("-topmost", True)
        tk.Label(self.win, text=prompt).pack(padx=10, pady=5)
        self.entry = tk.Entry(self.win, width=30)
        self.entry.pack(padx=10, pady=5)
        self.entry.focus_set()
        self.result = None
        tk.Button(self.win, text="确定", command=self._ok).pack(pady=5)
        self.win.wait_window()

    def _ok(self):
        self.result = self.entry.get()
        self.win.destroy()


def random_line(kind):
    import random
    return random.choice(config.TALKS.get(kind, config.TALKS["idle"]))
