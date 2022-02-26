import argparse
import sys
from .shared import eprint, glob_paths, read_lines, print_lines
import random
import re
from functools import cmp_to_key

NUM_RX = r'([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)'

def num_value(s):
    m = re.search(NUM_RX, s)
    if m:
        return float(m.group(1))

def cmp_numeric(s1, s2):
    if s1 == s2:
        return 0
    v1 = num_value(s1)
    v2 = num_value(s2)

    #print(v1, v2)

    if v1 is None and v2 is None:
        return -1 if s1 < s2 else 1
    if v1 is None:
        return -1
    if v2 is None:
        return 1
    if v1 == v2:
        return -1 if s1 < s2 else 1
    return -1 if v1 < v2 else 1
    
def main():
    parser = argparse.ArgumentParser(description='sorts lines')
    parser.add_argument('--numeric-sort', '-n', action='store_true')
    parser.add_argument('--reverse', '-r', action='store_true')
    parser.add_argument('--random-sort', '-R', action='store_true')
    parser.add_argument('--unique', '-u', action='store_true')
    parser.add_argument('path', nargs="*")

    args = parser.parse_args()
    paths = glob_paths(args.path)
    lines = read_lines(paths)
    
    if args.random_sort:
        lines = [(line, random.random()) for line in lines]
        lines.sort(key=lambda item: item[1])
        lines = [e[0] for e in lines]
    elif args.numeric_sort:
        lines.sort(key=cmp_to_key(cmp_numeric))
    else:
        lines.sort()

    if args.unique:
        res = [lines[0]]
        for line in lines:
            if line != res[-1]:
                res.append(line)
        lines = res

    if args.reverse:
        print_lines(reversed(lines))
    else:
        print_lines(lines)

if __name__ == "__main__":
    main()