from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

def create_image():
    width = 64
    height = 64
    color1 = "black"
    color2 = "white"

    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image

def on_activate(icon, item):
    print('Tray icon clicked!')

icon = Icon("MyApp", create_image(), menu=Menu(
    MenuItem('Activate', on_activate)
))

icon.run()
