from sys import argv


def parity(bits, ids):
    return str(len([1 for i in ids if bits[i] == "1"]) % 2)


def hamming(bits):
    p1 = parity(bits, [0, 1, 3])
    p2 = parity(bits, [0, 2, 3])
    p3 = parity(bits, [1, 2, 3])
    p = parity(p1 + p2 + bits[0] + p3 + bits[1:], range(7))

    return p1 + p2 + bits[0] + p3 + bits[1:] + p


if len(argv) != 3:
    print("not enough arguments")
    exit(1)

input_file = argv[1]
output_file = argv[2]

with open(input_file, "rb") as f:
    contents = f.read()

bitstring = ''.join("{0:08b}".format(byte) for byte in contents)

encoded = bytes(int(hamming(bitstring[i:i+4]), 2)
                    for i in range(0, len(bitstring), 4))


with open(output_file, "wb") as f:
    f.write(encoded)
