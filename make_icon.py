from PIL import Image
import os

img_path = "Images/MadotsukiDown1.png"
out_path = "icon.ico"

if os.path.exists(img_path):
    img = Image.open(img_path)
    # Resize to standard icon sizes
    icon_sizes = [(16,16), (32, 32), (48, 48), (64,64), (128, 128), (256, 256)]
    img.save(out_path, format="ICO", sizes=icon_sizes)
    print("Icon generated.")
else:
    print("Source image not found.")
