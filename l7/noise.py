from sys import argv
import random

if len(argv) != 4:
    print("not enough arguments")
    exit(1)

p = float(argv[1])
input_file = argv[2]
output_file = argv[3]

with open(input_file, "rb") as f:
    contents = f.read()

bitstring = ''.join("{0:08b}".format(byte) for byte in contents)
new_bitstring = ''.join(str(int(not int(bit)))
                        if random.random() <= p else bit for bit in bitstring)

output = bytes(int(new_bitstring[i:i+8], 2) for i in range(0, len(new_bitstring), 8))

with open(output_file, "wb") as f:
    f.write(output)