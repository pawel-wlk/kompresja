from sys import argv
from collections import defaultdict
from math import log


class Pixel:
    def __init__(self, red=0, green=0, blue=0):
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self):
        return f"{self.red} {self.green} {self.blue}"

    def __add__(self, other):
        return Pixel(red=self.red+other.red, green=self.green+other.green, blue=self.blue+other.blue)

    def __sub__(self, other):
        return Pixel(red=self.red-other.red, green=self.green-other.green, blue=self.blue-other.blue)

    def __floordiv__(self, num):
        return Pixel(red=self.red // num, green=self.green // num, blue=self.blue // num)

    def __mod__(self, num):
        return Pixel(
            red=self.red % num,
            green=self.green % num,
            blue=self.blue % num
        )


def parse_bitmap(bitmap, width, height):
    result = []
    row = []
    for i in range(width*height):
        row.append(Pixel(
            blue=bitmap[i*3],
            green=bitmap[i*3+1],
            red=bitmap[i*3+2],
        ))

        if len(row) == width:
            result.insert(0, row)
            row = []

    return result


def entropy(bitmap, color):
    occurences = defaultdict(int)
    count = 0
    for row in bitmap:
        for pixel in row:
            if color == 'red':
                occurences[pixel.red] += 1
                count += 1
            elif color == 'green':
                occurences[pixel.green] += 1
                count += 1
            elif color == 'blue':
                occurences[pixel.blue] += 1
                count += 1
            else:
                occurences[pixel.red] += 1
                occurences[pixel.green] += 1
                occurences[pixel.blue] += 1
                count += 3

    result = 0
    for val, c in occurences.items():
        result += c * log(c, 2)

    return log(count, 2) - (result / count)


def jpeg_ls(bitmap, prediction_scheme):
    empty = Pixel(red=0, green=0, blue=0)
    result = []
    for i, row in enumerate(bitmap):
        enc_row = []
        for j, pixel in enumerate(row):
            if i == 0:
                north = empty
            else:
                north = bitmap[i-1][j]

            if j == 0:
                west = empty
            else:
                west = bitmap[i][j-1]

            if i == 0 or j == 0:
                north_west = empty
            else:
                north_west = bitmap[i-1][j-1]

            encoding = (pixel - prediction_scheme(north,
                                                  west, north_west)) % 256
            enc_row.append(encoding)

        result.append(enc_row)

    return result


prediction_schemes = [
    lambda n, w, nw: w,
    lambda n, w, nw: n,
    lambda n, w, nw: nw,
    lambda n, w, nw: n+w-nw,
    lambda n, w, nw: n+(w-nw)//2,
    lambda n, w, nw: w+(n-nw)//2,
    lambda n, w, nw: ((n+w) % 256)//2,
    lambda n, w, nw: max(w, n) if nw >= max(
        w, n) else min(w, n) if nw <= min(w, n) else w+n-nw
]


def print_entropies(bitmap):
    print(f"General: {entropy(bitmap, '')}")
    print(f"Red: {entropy(bitmap, 'red')}")
    print(f"Green: {entropy(bitmap, 'green')}")
    print(f"Blue: {entropy(bitmap, 'blue')}")
    print('---')


def main():
    file = argv[1]

    with open(file, 'rb') as f:
        image = f.read()

    width = image[13]*256 + image[12]
    height = image[15]*256 + image[14]

    bitmap = parse_bitmap(image[18:-26], width, height)

    print('Image entropy')
    print_entropies(bitmap)

    for i, scheme in enumerate(prediction_schemes, 1):
        encoded = jpeg_ls(bitmap, scheme)
        print(f"Scheme {i}")
        print_entropies(encoded)


if __name__ == "__main__":
    main()
