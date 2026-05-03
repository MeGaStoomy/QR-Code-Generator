from PIL import Image

source = Image.open(r"other\icon-512.png")  # or your 256px source
sizeRange: range = range(256, 0, -1)

layers = [source.resize((s, s), Image.NEAREST) for s in sizeRange]

layers[0].save(
    r"icon.ico",
    format="ICO",
    sizes=[(s, s) for s in sizeRange],
    append_images=layers[1:]
)