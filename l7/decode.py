from sys import argv

codes = [
    "00000000",
    "11010010",
    "01010101",
    "10000111",
    "10011001",
    "01001011",
    "11001100",
    "00011110",
    "11100001",
    "00110011",
    "10110100",
    "01100110",
    "01111000",
    "10101010",
    "00101101",
    "11111111",
]

errors = 0

def decode(bits):
    for code in codes:
        diffs = 0
        for bit1, bit2 in zip(bits, code):
            if bit1 != bit2:
                diffs += 1

        if diffs in (0, 1):
            return code[2] + code[4] + code[5] + code[6]
        elif diffs == 2:
            global errors
            errors += 1
            return "0000"

    return "0000"


if len(argv) != 3:
    print("not enough arguments")
    exit(1)

input_file = argv[1]
output_file = argv[2]

with open(input_file, "rb") as f:
    contents = f.read()

decoded = ''.join(decode("{0:08b}".format(byte)) for byte in contents)

output = bytes(int(decoded[i:i+8], 2) for i in range(0, len(decoded), 8))
print(f'found 2 errors {errors} times')


with open(output_file, "wb") as f:
    f.write(output)
