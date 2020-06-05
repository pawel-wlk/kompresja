from sys import argv

if len(argv) != 3:
    print("not enough arguments")
    exit(1)

file1 = argv[1]
file2 = argv[2]


with open(file1, "rb") as f:
    contents = f.read()

bitstring1 = ''.join("{0:08b}".format(byte) for byte in contents)

with open(file2, "rb") as f:
    contents = f.read()

bitstring2 = ''.join("{0:08b}".format(byte) for byte in contents)


l = min(len(bitstring1), len(bitstring2))
size_diff = abs(len(bitstring1) - len(bitstring2)) // 4

diffs_count = len([1 for i in range(0, l, 4) if bitstring1[i:i+4] == bitstring2[i:i+4]])

print(diffs_count + size_diff)