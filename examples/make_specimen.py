"""Generate an original lettering test plate; no third-party art or fonts bundled.

Run from the repository: python examples/make_specimen.py OUTPUT_DIRECTORY
Then render examples/specimen.json with --background OUTPUT_DIRECTORY/plate.png.
"""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def main():
    p = argparse.ArgumentParser()
    p.add_argument("output", type=Path)
    p.add_argument("--font", required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", (1200, 1580), "#F4F1E9")
    d = ImageDraw.Draw(im)
    title = ImageFont.truetype(args.font, 46)
    small = ImageFont.truetype(args.font, 22)
    d.text((50, 28), "字里有声 / COMIC LETTERER", font=title, fill="#20202A")
    d.text(
        (52, 94),
        "原创排字标本 · 中文真字 · 矢量母版 · 800 px 阅读检查",
        font=small,
        fill="#535865",
    )
    labels = [
        "01  平静对白",
        "02  思想",
        "03  喊叫",
        "04  耳语",
        "05  虚弱",
        "06  设备声",
    ]
    for n, label in enumerate(labels):
        x = 40 + (n % 2) * 580
        y = 160 + (n // 2) * 340
        d.rounded_rectangle((x, y, x + 540, y + 320), radius=14, fill="#E4E8E7")
        d.text((x + 20, y + 16), label, font=small, fill="#535865")
        tx = x + 380
        ty = y + 290
        d.ellipse((tx - 5, ty - 5, tx + 5, ty + 5), fill="#367A79")
        d.text((tx + 14, ty - 13), "声源", font=small, fill="#367A79")
    d.rounded_rectangle((40, 1180, 1160, 1535), radius=14, fill="#E4E8E7")
    d.text((60, 1194), "07  连续发言 + 物件声音", font=small, fill="#535865")
    d.ellipse((275, 1490, 285, 1500), fill="#367A79")
    d.text((300, 1481), "声源", font=small, fill="#367A79")
    d.text(
        (50, 1545),
        "技术样式页，不代表所有漫画声线。圆点为显式声源坐标。",
        font=small,
        fill="#535865",
    )
    im.save(args.output / "plate.png")


if __name__ == "__main__":
    main()
