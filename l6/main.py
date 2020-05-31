import argparse
from itertools import chain


class Elias:
    def encode(self, number):
        code = bin(number)[2:]
        code = "0" * (len(code) - 1) + code
        return code

    def decode(self, code):
        codes = []
        counter = 0
        idx = 0
        while idx < len(code):
            if code[idx] == "0":
                counter += 1
                idx += 1
            else:
                codes.append(int(code[idx: idx + counter + 1], base=2))
                idx += counter + 1
                counter = 0
        return codes


class Pixel:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __add__(self, other):
        return Pixel(
            self.red + other.red, self.green + other.green, self.blue + other.blue
        )

    def __sub__(self, other):
        return Pixel(
            self.red - other.red, self.green - other.green, self.blue - other.blue
        )

    def __mul__(self, number):
        return Pixel(self.red * number, self.green * number, self.blue * number)

    def __div__(self, number):
        return Pixel(self.red / number, self.green / number, self.blue / number)

    def __floordiv__(self, number):
        return Pixel(self.red // number, self.green // number, self.blue // number)

    def __mod__(self, number):
        return Pixel(self.red % number, self.green % number, self.blue % number)

    def quantify(self, step):
        r = int(self.red // step * step)
        g = int(self.green // step * step)
        b = int(self.blue // step * step)
        return Pixel(r, g, b)


class Bitmap:
    def __init__(self, bitmap, width, height):
        self.width = width
        self.height = height

        result = []
        row = []
        for i in range(width * height):
            row.append(
                Pixel(
                    blue=bitmap[i * 3], green=bitmap[i *
                                                     3 + 1], red=bitmap[i * 3 + 2]
                )
            )

            if width == len(row):
                result.insert(0, row)
                row = []
        self.bitmap = result

    def __getitem__(self, pos):
        x, y = pos
        ret_x, ret_y = x, y
        if x < 0:
            ret_x = 0
        elif x >= self.width:
            ret_x = self.width - 1

        if y < 0:
            ret_y = 0
        elif y >= self.height:
            ret_y = self.height - 1

        return self.bitmap[ret_y][ret_x]


def parse_bitmap(bitmap, width, height):
    result = []
    row = []

    for i in range(width * height):
        row.append(
            Pixel(blue=bitmap[i * 3], green=bitmap[i * 3 + 1],
                  red=bitmap[i * 3 + 2])
        )

        if len(row) == width:
            result.insert(0, row)
            row = []

    return result


def filter(bitmap, x, y, high=False):
    weights_low = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    wegihts_high = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]

    weights = wegihts_high if high else weights_low

    pix = Pixel(0, 0, 0)
    for i in range(3):
        for j in range(3):
            pix += bitmap[x + i - 1, y + j - 1] * weights[i][j]

    weights_sum = sum(sum(row) for row in weights)

    if weights_sum <= 0:
        weights_sum = 1

    pix = pix // weights_sum

    pix.red *= (pix.red > 0)
    pix.green *= (pix.green > 0)
    pix.blue *= (pix.blue > 0)

    pix.red = 255 if pix.red > 255 else pix.red
    pix.green = 255 if pix.green > 255 else pix.green
    pix.blue = 255 if pix.blue > 255 else pix.blue
    pix.red = 255 + (pix.red-255) * (pix.red < 255)

    return pix


def bitmap_to_array(bitmap):
    return chain.from_iterable((pixel.blue, pixel.green, pixel.red) for pixel in bitmap)


def differential_coding(bitmap):
    prev = bitmap[0]
    result = [prev]
    for pixel in bitmap[1:]:
        prev = pixel - prev
        result.append(prev)
        prev = pixel

    return result


def differential_decoding(diffs):
    prev = diffs[0]
    result = [prev]
    for x in diffs[1:]:
        prev = prev + x
        result.append(prev)
    return result


def quantify(bitmap, k):
    step = 256 // (2 ** k)
    return [pixel.quantify(step) for pixel in bitmap]


def encode(bitmap, k):
    filtered_low = [
        filter(bitmap, x, y)
        for y in reversed(range(bitmap.height))
        for x in range(bitmap.width)
    ]
    filtered_high = [
        filter(bitmap, x, y, True)
        for y in reversed(range(bitmap.height))
        for x in range(bitmap.width)
    ]

    low = differential_coding(filtered_low)
    byte_array = bitmap_to_array(low)

    byte_array = [2 * x if x > 0 else abs(x) * 2 + 1 for x in byte_array]

    bitstring = "".join(Elias().encode(x) for x in byte_array)
    if len(bitstring) % 8 != 0:
        bitstring += "0" * (8 - (len(bitstring) % 8))

    b = bytes(int(bitstring[i: i + 8], 2) for i in range(0, len(bitstring), 8))

    quantified = quantify(filtered_high, k)
    quantified_bytes = bytes(bitmap_to_array(quantified))

    bitmap = [
        bitmap[x, y]
        for y in reversed(range(bitmap.height))
        for x in range(bitmap.width)
    ]

    print("Low")
    calculate_parameters(bitmap, filtered_low)
    print("High")
    calculate_parameters(bitmap, quantified)

    return b, quantified_bytes


def decode(payload_low):
    hexstring = payload_low.hex()
    bitstring = "".join(
        "{0:08b}".format(int(hexstring[x: x + 2], base=16))
        for x in range(0, len(hexstring), 2)
    )

    codes = Elias().decode(bitstring)
    diffs = [x // 2 if x % 2 == 0 else -(x // 2) for x in codes]

    bitmap = [
        Pixel(int(diffs[i + 2]), int(diffs[i + 1]), int(diffs[i]))
        for i in range(0, len(diffs), 3)
    ]
    bitmap = differential_decoding(bitmap)
    bitmap = bitmap_to_array(bitmap)

    return bytes(bitmap)


def distance_squared(a, b):
    return (a - b) ** 2


def mse(original, new):
    return (1 / len(original)) * sum([distance_squared(a, b) for a, b in zip(original, new)])


def snr(x, mserr):
    return ((1 / len(x)) * sum([distance_squared(i, 0) for i in x])) / mserr


def calculate_parameters(original, new):
    original_array = []
    for pixel in original:
        original_array += [pixel.blue, pixel.green, pixel.red]

    original_red = [pixel.red for pixel in original]
    original_green = [pixel.green for pixel in original]
    original_blue = [pixel.blue for pixel in original]

    new_array = []
    for pixel in new:
        new_array += [pixel.blue, pixel.green, pixel.red]

    new_red = [pixel.red for pixel in new]
    new_green = [pixel.green for pixel in new]
    new_blue = [pixel.blue for pixel in new]

    mserr = mse(original_array, new_array)
    mserr_red = mse(original_red, new_red)
    mserr_green = mse(original_green, new_green)
    mserr_blue = mse(original_blue, new_blue)
    snratio = snr(original_array, mserr)

    print("MSE:", mserr)
    print("MSE (red):", mserr_red)
    print("MSE (green):", mserr_green)
    print("MSE (blue):", mserr_blue)
    print("SNR:", snratio)


def main():
    parser = argparse.ArgumentParser('encode/decode tga files')
    parser.add_argument('file')
    parser.add_argument('--k', dest='k', default=2)
    parser.add_argument('--encode', dest='encode',
                        action='store_true', default=True)
    parser.add_argument('--decode', dest='encode',
                        action='store_false', default=True)
    parser.add_argument('--parameters', dest='encode',
                        action='store_false', default=True)

    args = parser.parse_args()

    with open(args.file, "rb") as f:
        tga = f.read()
        header = tga[:18]
        footer = tga[len(tga) - 26:]
        width = tga[13] * 256 + tga[12]
        height = tga[15] * 256 + tga[14]

    if args.encode:
        bitmap = Bitmap(tga[18: len(tga) - 26], width, height)

        b, quantified = encode(bitmap, args.k)

        with open("output_low_encoded", "wb") as f:
            f.write(header + b + footer)
        with open("output_high_encoded.tga", "wb") as f:
            f.write(header + quantified + footer)

    else:
        payload = tga[18:-26]

        bitmap = decode(payload)

        with open("output_low_decoded.tga", "wb") as f:
            f.write(header + bitmap + footer)


if __name__ == "__main__":
    main()
