import argparse
from bashrange import expand_args
from .shared import has_magic
import glob
import os
import re
from collections import defaultdict
from . import format_size

def int_ceil(num, den):
    return (num + den - 1) // den

def split_path(path):
    x = re.split("[\\\\/]", path)
    if re.match('^[a-z]:$', x[0], re.IGNORECASE):
        x[0] = x[0] + "\\"
    return x

def print_bytes(size, path):
    print("{:16d} {}".format(size, path))

def print_human(size, path):
    print("{} {}".format(format_size(size, 16), path))

def main():
    EXAMPLE_TEXT = """examples:
"""
    parser = argparse.ArgumentParser(add_help=False, prog="", description="", epilog=EXAMPLE_TEXT, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('path', nargs='*')
    parser.add_argument('-s', action='store_true', help='print summary only')
    parser.add_argument('-f', action='store_true', help='print files stat')
    parser.add_argument('-d', action='store_true', help='print directories stat')
    parser.add_argument('-h', action='store_true', help='print in human friendly units (KB, MB, GB, TB)')
    parser.add_argument('--help', action='help')
    
    args = parser.parse_args(expand_args())

    if not args.d and not args.f:
        args.s = True

    if args.h:
        print_fn = print_human
    else:
        print_fn = print_bytes

    paths = []
    for path in args.path:
        if has_magic(path):
            for e in glob.glob(path):
                if not os.path.isfile(e):
                    paths.append(e)
        else:
            if not os.path.exists(path):
                raise ValueError("Path does not exist {}".format(path))
            if os.path.isfile(path):
                continue
            paths.append(path)

    for path in paths:
        stat = defaultdict(lambda: 0)
        n1 = len(split_path(path))
        for root, dirs, files in os.walk(path):
            for d in dirs:
                p = os.path.join(root, d)
                stat[p] = 0

            for f in files:
                p = os.path.join(root, f)
                p_ = split_path(p)
                s = os.path.getsize(p)
                for i in range(n1, len(p_)):
                    sp = os.path.join(*p_[0:i])
                    #print(sp)
                    stat[sp] += s
                if args.f:
                    print_fn(s, p)
            
        if args.s:
            print_fn(stat[path], path)
        elif args.d:
            ks = list(stat.keys())
            ks.sort()
            for k in ks:
                print_fn(stat[k], k)

if __name__ == "__main__":
    main()