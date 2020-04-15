import argparse
from itertools import chain


class EliasGamma:
    def encode(self, num: int):
        binary = bin(num)[2:]
        return (len(binary)-1) * '0' + binary

    def decode(self, bits):
        while bits != "":
            zeros_count = 0
            while bits[zeros_count] == '0':
                zeros_count += 1
                if zeros_count >= len(bits):
                    return

            yield int(bits[:2*zeros_count+1], base=2)
            bits = bits[2*zeros_count+1:]


class EliasDelta:
    def encode(self, num: int):
        binary = bin(num)[2:]
        n = EliasGamma().encode(len(binary))

        return n + binary[1:]

    def decode(self, bits):
        while bits != "":
            zeros_count = 0
            while bits[zeros_count] == '0':
                zeros_count += 1
                if zeros_count >= len(bits):
                    return

            n = int(bits[:2*zeros_count+1], base=2)
            bits = bits[2*zeros_count+1:]

            yield int('1' + bits[:n-1], base=2)
            bits = bits[n-1:]


class EliasOmega:
    def encode(self, num: int):
        encoding = '0'
        k = num

        while k > 1:
            binary_k = bin(k)[2:]
            encoding = binary_k + encoding
            k = len(binary_k) - 1

        return encoding

    def decode(self, bits):
        while bits != "":
            n = 1
            if bits[0] == '0':
                return
            while bits[0] != '0':
                prev_n = n
                n = int(bits[:n+1], base=2)
                bits = bits[prev_n+1:]
                if bits == "":
                    return

            yield n
            bits = bits[1:]


class Encoding:
    def __init__(self, number_encoder):
        self.number_encoder = number_encoder

    def lzw_encode(self, string: str):
        encoding_table = {chr(i): i for i in range(256)}

        next_num = 256

        prev = string[0]
        for char in string[1:]:
            if (prev + char) in encoding_table:
                prev += char
            else:
                yield encoding_table[prev]

                encoding_table[prev + char] = next_num
                next_num += 1

                prev = char

        yield encoding_table[prev]

    def lzw_decode(self, codes):
        decoding_table = {i: chr(i) for i in range(256)}
        next_num = 256

        old = codes[0]
        c = ""
        yield decoding_table[old]

        for code in codes[1:]:
            if code not in decoding_table:
                s = decoding_table[old]
                s += c
            else:
                s = decoding_table[code]

            yield s
            c = s[0]
            decoding_table[next_num] = decoding_table[old] + c
            next_num += 1

            old = code

    def encode(self, string):
        bits = ''.join(self.number_encoder.encode(num)
                       for num in self.lzw_encode(string))

        return ''.join(bits)

    def decode(self, bits):
        return ''.join(self.lzw_decode(list(self.number_encoder.decode(bits))))


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--encoding', dest='encoding',
                        choices=['omega', 'gamma', 'delta', 'fibonacci'], default='omega')
    parser.add_argument('-e', '--encode', dest='encode',
                        action='store_true', default=True)
    parser.add_argument('-d', '--decode', dest='encode', action='store_false')
    parser.add_argument('infile')
    parser.add_argument('outfile')

    return parser


def main():
    args = get_arg_parser().parse_args()

    if args.encoding == 'gamma':
        number_encoder = EliasGamma()
    elif args.encoding == 'delta':
        number_encoder = EliasDelta()
    else:
        number_encoder = EliasOmega()

    encoding = Encoding(number_encoder)

    if args.encode:
        with open(args.infile, 'r') as f:
            text = f.read()
        result = encoding.encode(text)

        with open(args.outfile, 'w') as f:
            f.write(result)
    else:
        with open(args.infile, 'r') as f:
            bits = f.read()
        result = encoding.decode(bits)

        with open(args.outfile, 'w') as f:
            f.write(result)


if __name__ == "__main__":
    main()