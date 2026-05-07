"""生成 AuraTasks Pro 应用图标 - 高质量多尺寸 ICO"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 圆角矩形背景 (Monokai Pro 绿色 #A6E22A)
    padding = int(size * 0.06)
    radius = int(size * 0.2)
    bg_box = [padding, padding, size - padding, size - padding]
    draw.rounded_rectangle(bg_box, radius=radius, fill=(166, 226, 42, 255))

    # 中心对勾
    cx, cy = size // 2, size // 2
    s = size / 256.0  # 缩放因子
    p1 = (int(cx - 36*s), int(cy + 4*s))
    p2 = (int(cx - 8*s), int(cy + 32*s))
    p3 = (int(cx + 40*s), int(cy - 26*s))
    w = max(int(18 * s), 2)
    draw.line([p1, p2], fill=(45, 45, 45, 255), width=w)
    draw.line([p2, p3], fill=(45, 45, 45, 255), width=w)

    return img

out_dir = r"E:\Python code\taskmanager\aura_tasks_pro\resources"

# 生成多尺寸
sizes = [(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]
images = [create_icon(s[0]) for s in sizes]

# 保存 PNG
png_path = os.path.join(out_dir, "app_icon.png")
images[-1].save(png_path, 'PNG')
print(f"PNG saved: {png_path}")

# 保存 ICO
ico_path = os.path.join(out_dir, "app_icon.ico")
images[-1].save(
    ico_path,
    format='ICO',
    sizes=sizes,
    append_images=images[:-1],
)
print(f"ICO saved: {ico_path} ({os.path.getsize(ico_path)} bytes)")

# 验证
ico = Image.open(ico_path)
print(f"ICO sizes: {ico.info.get('sizes', 'N/A')}")
