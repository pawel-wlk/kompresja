import argparse
import sys
from collections import defaultdict
from math import log


class Node:
    def __init__(self, parent=None, left=None, right=None, weight=0, symbol=''):
        self.parent = parent
        self.left = left
        self.right = right
        self.weight = weight
        self.symbol = symbol

class AdaptiveHuffman:
    def __init__(self):
        self.NYT = Node(symbol="NYT")
        self.root = self.NYT
        self.nodes = []
        self.seen = [None for _ in range(256)]

    def get_code(self, s, node, code=''):
        if node.left is None and node.right is None:
            return code if node.symbol == s else ''
        else:
            tmp = ''
            if node.left is not None:
                tmp = self.get_code(s, node.left, code+'0')
            if not tmp and node.right is not None:
                tmp = self.get_code(s, node.right, code+'1')

            return tmp

    def find_largest_node(self, weight):
        for n in reversed(self.nodes):
            if n.weight == weight:
                return n

    def swap_node(self, n1, n2):
        i1, i2 = self.nodes.index(n1), self.nodes.index(n2)
        self.nodes[i1], self.nodes[i2] = self.nodes[i2], self.nodes[i1]

        n1.parent, n2.parent = n2.parent, n1.parent

        if n1.parent.left is n2:
            n1.parent.left = n1
        else:
            n1.parent.right = n1

        if n2.parent.left is n1:
            n2.parent.left = n2
        else:
            n2.parent.right = n2

    def insert(self, s):
        node = self.seen[ord(s)]

        if node is None:
            new = Node(symbol=s, weight=1)
            internal = Node(weight=1, parent=self.NYT.parent, left=self.NYT, right=new)
            new.parent = internal
            self.NYT.parent = internal

            if internal.parent is not None:
                internal.parent.left = internal
            else:
                self.root = internal

            self.nodes.insert(0, internal)
            self.nodes.insert(0, new)

            self.seen[ord(s)] = new
            node = internal.parent

        while node is not None:
            largest = self.find_largest_node(node.weight)

            if node is not largest and node is not largest.parent and largest is not node.parent:
                self.swap_node(node, largest)

            node.weight += 1
            node = node.parent


    def encode(self, text):
        result = ''

        for s in text:
            if self.seen[ord(s)]:
                result += self.get_code(s, self.root)
            else:
                result += self.get_code('NYT', self.root)
                result += bin(ord(s))[2:].zfill(8)
                
            self.insert(s)

        return result

    def get_ascii_symbol(self, binary_string):
        return chr(int(binary_string, 2))

    def decode(self, text):
        result = ''

        symbol = self.get_ascii_symbol(text[:8])
        result += symbol

        self.insert(symbol)
        node = self.root

        i = 8
        while i < len(text):
            node = node.left if text[i] == '0' else node.right
            symbol = node.symbol

            if symbol:
                if symbol == 'NYT':
                    symbol = self.get_ascii_symbol(text[i+1:i+9])
                    i += 8

                result += symbol
                self.insert(symbol)
                node = self.root

            i += 1

        return result


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--encode', dest='encode', action='store_true', default=True)
    parser.add_argument('-d', '--decode', dest='encode', action='store_false')
    parser.add_argument('input_file')
    parser.add_argument('output_file')

    return parser

def write_bits(bits, file):
    with open(file, 'wb') as f:
        for i in range(0, len(bits), 8):
            f.write(int(bits[i:i+8].zfill(8), 2).to_bytes(1, 'big'))

def entropy(string):
    char_occurences = defaultdict(int)
    for char in string:
        char_occurences[char] += 1

    result = 0
    for char, count in char_occurences.items():
        result += count * log(count, 2)

    char_count = len(string)

    return log(char_count, 2) - (result / char_count)


def main():
    args = get_arg_parser().parse_args()

    with open(args.input_file) as f:
        text = f.read()


    if args.encode:
        result = AdaptiveHuffman().encode(text)
        print('Entropy:', entropy(text))
        print('Average length:', len(result) / len(text))
        print('Compression ratio:', len(text) * 8 / len(result))
    else:
        result = AdaptiveHuffman().decode(text)

    with open(args.output_file, 'w') as f:
        f.write(result)


if __name__ == "__main__":
    main()
        


    

        