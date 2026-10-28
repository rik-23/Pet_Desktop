"""渲染：生成/加载宠物帧、绘制脚印、影子。"""
import os
import math
from PIL import Image, ImageDraw
import config


def make_frame(state, skin="penguin", idx=0, size=config.PET_SIZE):
    """代码绘制 Q 版宠物帧（无图片素材时降级使用）。"""
    c = config.SKINS.get(skin, config.SKINS["penguin"])
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2 + 4
    # 身体
    d.ellipse([cx - 30, cy - 36, cx + 30, cy + 38], fill=c["body"] + (255,))
    d.ellipse([cx - 18, cy - 16, cx + 18, cy + 34], fill=c["belly"] + (255,))
    # 眼睛
    for ex in (-11, 11):
        d.ellipse([cx + ex - 8, cy - 22, cx + ex + 8, cy - 6], fill=(255, 255, 255, 255))
        d.ellipse([cx + ex - 4, cy - 18, cx + ex + 4, cy - 10], fill=(30, 30, 40, 255))
    # 腮红
    d.ellipse([cx - 22, cy - 4, cx - 12, cy + 4], fill=(255, 150, 150, 120))
    d.ellipse([cx + 12, cy - 4, cx + 22, cy + 4], fill=(255, 150, 150, 120))
    # 嘴
    if skin in ("cat", "dog"):
        d.ellipse([cx - 4, cy - 2, cx + 4, cy + 5], fill=c["beak"] + (255,))
    else:
        d.polygon([cx - 6, cy - 2, cx + 6, cy - 2, cx, cy + 6], fill=c["beak"] + (255,))
    # 脚
    swing = 5 if idx % 2 == 0 else -5
    d.ellipse([cx - 15 + swing, cy + 36, cx - 3 + swing, cy + 46], fill=c["beak"] + (255,))
    d.ellipse([cx + 3 - swing, cy + 36, cx + 15 - swing, cy + 46], fill=c["beak"] + (255,))
    if state == "sleep":
        d.text((cx + 20, cy - 36), "Z", fill=(150, 150, 150, 255))
    return img


def load_or_make(state, skin, idx, size):
    """优先加载 frames/<skin>_<state>_<idx>.png，否则代码生成。"""
    path = os.path.join(config.APP_DIR, "frames", f"{skin}_{state}_{idx}.png")
    if os.path.exists(path):
        try:
            return Image.open(path).convert("RGBA")
        except Exception:
            pass
    return make_frame(state, skin, idx, size)


def rotate_image(img, angle):
    if not angle:
        return img
    return img.rotate(angle, expand=False, resample=Image.BICUBIC)


def draw_shadow(canvas, x0, y0, x1, y1):
    """躲藏时的半透明影子（窗口内坐标）。"""
    canvas.create_oval(x0, y0, x1, y1, fill="#555555", stipple="gray25", outline="")
