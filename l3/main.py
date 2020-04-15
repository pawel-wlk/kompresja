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


class Fibonacci:
    def __init__(self):
        self._sequence = [0, 1]
        self._prev_max = 1

    def _get_sequence(self, max_num):
        if max_num > self._prev_max:
            while self._sequence[-1] + self._sequence[-2] <= max_num:
                self._sequence.append(self._sequence[-1] + self._sequence[-2])

            self._prev_max = max_num

            return self._sequence.copy()
        else:
            return [num for num in self._sequence if num <= max_num]

    def encode(self, num):
        sequence = self._get_sequence(num)
        result = '1'

        while num != 0:
            num -= sequence[-1]
            result = '1' + result
            sequence.pop()
            while sequence[-1] > num:
                result = '0' + result
                sequence.pop()

        return result[1:]

    def decode(self, bits):
        cur_num = 0
        prev_bit = ''
        cur_fib = 1
        prev_fib = 1

        for bit in bits:
            if bit == prev_bit and prev_bit == '1':
                yield cur_num
                cur_num = 0
                prev_bit = ''
                cur_fib = 1
                prev_fib = 1
            else:
                cur_num += int(bit) * cur_fib
                prev_fib, cur_fib = cur_fib, cur_fib + prev_fib
                prev_bit = bit


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
        return ''.join(self.number_encoder.encode(num)
                       for num in self.lzw_encode(string))

    def decode(self, bits):
        return ''.join(self.lzw_decode(list(self.number_encoder.decode(bits))))


def write_bits(bits, file):
    padding = (8 - ((len(bits) + 3) % 8)) % 8
    output = bin(padding)[2:].zfill(3) + bits + padding*'0'
    bytes_arr = bytes(int(output[i:i+8], 2) for i in range(0, len(output), 8))

    with open(file, 'wb') as f:
        f.write(bytes_arr)


def read_bits(file):
    with open(file, 'rb') as f:
        bits = ''.join(bin(byte)[2:].zfill(8) for byte in f.read())
    padding_len = int(bits[:3], 2)

    if padding_len == 0:
        return bits[3:]
    else:
        return bits[3:-padding_len]


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

    if args.encoding == 'fibonacci':
        number_encoder = Fibonacci()
    elif args.encoding == 'gamma':
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

        # with open(args.outfile, 'w') as f:
        #     f.write(result)
        write_bits(result, args.outfile)
    else:
        # with open(args.infile, 'r') as f:
        #     bits = f.read()
        bits = read_bits(args.infile)
        result = encoding.decode(bits)

        with open(args.outfile, 'w') as f:
            f.write(result)


if __name__ == "__main__":
    main()
