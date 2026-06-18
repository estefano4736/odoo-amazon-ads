import os
from PIL import Image

brain_dir = "/Users/estefanomacedo/.gemini/antigravity/brain/17c3816f-b3a5-4357-9dbd-74deb4dc5ec3"
img_path = os.path.join(brain_dir, "media_cropped_token_top.png")
img = Image.open(img_path)

# Y-ranges for the 5 lines
y_ranges = [
    (38, 58),   # Line 1
    (54, 74),   # Line 2
    (71, 91),   # Line 3
    (88, 108),  # Line 4
    (107, 127)  # Line 5
]

x_segments = [
    (0, 300),
    (250, 550),
    (500, 800),
    (750, 1004)
]

for line_idx, (y_min, y_max) in enumerate(y_ranges):
    line_num = line_idx + 1
    for seg_idx, (x_min, x_max) in enumerate(x_segments):
        seg_num = seg_idx + 1
        box = (x_min, y_min, x_max, y_max)
        cropped = img.crop(box)
        # 5x upscale using LANCZOS filter for clarity
        upscaled = cropped.resize((cropped.width * 5, cropped.height * 5), Image.LANCZOS)
        out_name = f"line{line_num}_seg{seg_num}.png"
        out_path = os.path.join(brain_dir, out_name)
        upscaled.save(out_path)
        print(f"Saved {out_name} (box: {box})")
