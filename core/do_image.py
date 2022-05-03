import base64
import io
import random
from io import BytesIO
from PIL import Image


def do_random_image(width: int, height: int):
    r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    image = Image.new('RGB', (width, height), (r, g, b))
    im_file = BytesIO()
    image.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()
    im_b64 = base64.b64encode(im_bytes)
    return im_b64


def do_user_image(size: tuple, image: bytes):
    image = Image.open(io.BytesIO(image))
    image = image.convert('RGB')
    img_size = image.size
    x = int(img_size[0]) // 4
    if x * 3 > img_size[1]:
        x = int(img_size[1]) // 3
    image = image.crop((0, 0, int(x * 4), int(x * 3)))
    image.thumbnail(size, Image.ANTIALIAS)
    im_file = BytesIO()
    image.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()
    im_b64 = base64.b64encode(im_bytes)
    return im_b64
