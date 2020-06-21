"""
This module contains utils to convert the map into an image.
"""
from PIL import Image, ImageDraw


class MapImageGenerator:
    @staticmethod
    def main():
        # make a blank image for the text, initialized to transparent text color
        txt = Image.new("RGBA", (200, 200), (255, 255, 255, 0))

        # get a drawing context
        d = ImageDraw.Draw(txt)
        d.rectangle([(2, 2), (48, 48)], outline=(50, 50, 50), width=2)
        d.rectangle([(52, 52), (98, 98)], outline=(50, 50, 50), width=2)
        d.rectangle([(152, 152), (198, 198)], outline=(50, 50, 50), width=2)

        txt.show()
