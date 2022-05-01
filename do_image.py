import base64
import random
from io import BytesIO
from PIL import Image


def do_random_image(width, height):
    r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    image = Image.new('RGB', (width, height), (r, g, b))
    im_file = BytesIO()
    image.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()
    im_b64 = base64.b64encode(im_bytes)
    return im_b64


def do_user_image(size: tuple, image):
    image = Image.open()



if __name__ == '__main__':
    image = do_image(500, 500)
    print(image)
