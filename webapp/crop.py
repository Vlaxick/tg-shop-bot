import os

from PIL import Image

img_path = "/Users/macbook/.gemini/antigravity-ide/brain/69fce9ea-b6d2-416e-91bc-985571a674a8/.user_uploaded/media_1788448908949.png"
if not os.path.exists(img_path):
    print("Not found")
    exit(1)

img = Image.open(img_path)

# Approximate coordinates for the 4 grid items (assuming 578x1024 size)
# Let's just crop out the inner colored rectangles.
# The grid has 2 columns.
# We'll just define the bounding boxes roughly.
box1 = (50, 110, 270, 330) # Top left
box2 = (300, 110, 520, 330) # Top right
box3 = (50, 500, 270, 720) # Bottom left
box4 = (300, 500, 520, 720) # Bottom right

os.makedirs("public/assets", exist_ok=True)

img.crop(box1).save("public/assets/icecream.png")
img.crop(box2).save("public/assets/papakha.png")
img.crop(box3).save("public/assets/cigar.png")
img.crop(box4).save("public/assets/brownie.png")

print("Done")
