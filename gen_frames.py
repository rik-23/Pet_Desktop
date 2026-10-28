"""导出程序生成的各皮肤帧图到 frames/，方便后续替换成好看的素材"""
import os
from PIL import Image, ImageDraw

SIZE = 100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")
os.makedirs(OUT, exist_ok=True)

SKINS = {
    "penguin": {"body": (43, 43, 43), "belly": (255, 255, 255)},
    "cat":     {"body": (180, 160, 140), "belly": (240, 230, 220)},
    "dog":     {"body": (150, 110, 70), "belly": (230, 210, 180)},
    "dino":    {"body": (80, 170, 90), "belly": (200, 240, 200)},
}


def make_frame(state, idx, skin="penguin"):
    cfg = SKINS.get(skin, SKINS["penguin"])
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = SIZE // 2, SIZE // 2
    d.ellipse([cx - 25, cy - 35, cx + 25, cy + 32], fill=cfg["body"] + (255,))
    d.ellipse([cx - 16, cy - 15, cx + 16, cy + 30], fill=cfg["belly"] + (255,))
    if skin in ("cat", "dog"):
        d.polygon([cx - 25, cy - 35, cx - 10, cy - 45, cx - 5, cy - 32], fill=cfg["body"] + (255,))
        d.polygon([cx + 25, cy - 35, cx + 10, cy - 45, cx + 5, cy - 32], fill=cfg["body"] + (255,))
    d.ellipse([cx - 12, cy - 22, cx - 6, cy - 15], fill=(255, 255, 255, 255))
    d.ellipse([cx + 6, cy - 22, cx + 12, cy - 15], fill=(255, 255, 255, 255))
    d.ellipse([cx - 10, cy - 20, cx - 8, cy - 17], fill=(0, 0, 0, 255))
    d.ellipse([cx + 8, cy - 20, cx + 10, cy - 17], fill=(0, 0, 0, 255))
    if skin in ("cat", "dog"):
        d.ellipse([cx - 4, cy - 10, cx + 4, cy - 6], fill=(0, 0, 0, 255))
    else:
        d.polygon([cx - 6, cy - 12, cx + 6, cy - 12, cx, cy - 6], fill=(255, 165, 0, 255))
    if skin == "dino":
        for k in range(-2, 3):
            d.polygon([cx + k * 9, cy - 35, cx + k * 9 - 4, cy - 28, cx + k * 9 + 4, cy - 28],
                      fill=(40, 120, 50, 255))
    swing = 6 if idx % 2 == 0 else -6
    if state == "sleep":
        d.ellipse([cx - 18, cy + 30, cx - 2, cy + 40], fill=(255, 165, 0, 255))
        d.ellipse([cx + 2, cy + 30, cx + 18, cy + 40], fill=(255, 165, 0, 255))
        d.text((cx + 18, cy - 30), "Z", fill=(120, 120, 120, 255))
    else:
        d.ellipse([cx - 14 + swing, cy + 30, cx - 4 + swing, cy + 38], fill=(255, 165, 0, 255))
        d.ellipse([cx + 4 - swing, cy + 30, cx + 14 - swing, cy + 38], fill=(255, 165, 0, 255))
    return img


for skin in SKINS:
    for st in ("walk", "idle", "sleep"):
        n = 4 if st == "walk" else 2
        for i in range(n):
            make_frame(st, i, skin).save(os.path.join(OUT, f"{skin}_{st}_{i}.png"))
print("已生成所有皮肤帧图到", OUT)
