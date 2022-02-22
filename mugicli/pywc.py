import enum
import fileinput
import argparse
import sys
import re
import math
import glob
from types import prepare_class
from .shared import glob_paths, read_bytes

def main():

    description='calculates number or lines words, chars and bytes in files'
    epilog='examples:\n  wc -l text.txt'

    parser = argparse.ArgumentParser(epilog=epilog, description=description, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-l', action='store_true', help='print the newline counts')
    parser.add_argument('-w', action='store_true', help='print the word counts')
    parser.add_argument('-m', action='store_true', help='print the character counts')
    parser.add_argument('-c', action='store_true', help='print the byte counts')
    parser.add_argument('path', nargs="*")

    args = parser.parse_args()

    def count_lines(data, path, res):
        text = ''
        try:
            text = data.decode('utf-8')
        except Exception as e:
            print(e)
        c = len(data)
        m = len(text)
        w = len(re.split('\\s+',text.strip()))
        l = len(text.split('\n'))
        res.append((l, w, m, c, path))

    res = []
    stdin_mode = len(args.path) == 0

    paths = glob_paths(args.path)

    if stdin_mode:
        data = sys.stdin.buffer.read()
        count_lines(data, '', res)
    else:
        for path in paths:
            count_lines(read_bytes(path), path, res)

    lt = sum([e[0] for e in res])
    wt = sum([e[1] for e in res])
    mt = sum([e[2] for e in res])
    ct = sum([e[3] for e in res])

    lw = len(str(lt))
    ww = len(str(wt))
    mw = len(str(mt))
    cw = len(str(ct))

    fmt = " ".join(['{:' + str(lw) + 'd}' if args.l else ''] +
        ['{:' + str(ww) + 'd}' if args.w else ''] +
        ['{:' + str(mw) + 'd}' if args.m else ''] +
        ['{:' + str(cw) + 'd}' if args.c else ''] +
        ['{}'])

    #print(fmt)

    if len(res) > 1:
        res.append((lt,wt,mt,ct,'total'))

    for item in res:
        cols = [v for v, en in zip(item, [args.l, args.w, args.m, args.c, True]) if en]
        print(fmt.format(*cols))

if __name__ == "__main__":
    main()