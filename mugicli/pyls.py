import argparse
from .shared import glob_paths, has_magic, debug_print
import glob
import os
import sys
from . import chunks, print_utf8
import math
from bashrange import expand_args
import shutil
import math
import re

def make_grid(ns, cols, rows):
    res = [[] for col in range(cols)]
    for i, n in enumerate(ns):
        #row = i % rows
        col = i // rows
        res[col].append(n)
    ls = [max([len(n) for n in col]) if len(col) else 0 for col in res]
    return res, ls, sum(ls) + (len(ls) - 1) * 2

def padded(n, l):
    return n + (' ' * (l - len(n)))

def print_grid(grid, ls):
    rows = len(grid[0])
    for row in range(rows):
        line = []
        for col, l in enumerate(ls):
            t = grid[col][row] if row < len(grid[col]) else ''
            line.append(padded(t, l))
        print_utf8('  '.join(line))

import datetime

def getmtime(path):
    mtime = os.path.getmtime(path)
    return datetime.datetime.fromtimestamp(mtime)
    
def getsize(path):
    return os.path.getsize(path)

def main():
    parser = argparse.ArgumentParser(description='lists directory')
    parser.add_argument('path', nargs='*')
    parser.add_argument("-1", action='store_true', dest='one')
    parser.add_argument("-a", action='store_true')
    parser.add_argument("-l", action='store_true')
    args = parser.parse_args(expand_args())

    if len(args.path) == 0:
        paths = ['.']
    else:
        paths = args.path

    header = len(paths) > 1

    isatty = sys.stdout.isatty()

    def tailslash(path, n):
        if os.path.isdir(os.path.join(path, n)):
            return n + "\\"
        return n
    
    def trimslash(n):
        if n.endswith('\\'):
            return n[:-1]
        return n

    for path in paths:
        if header:
            print_utf8(path)
        ns = [tailslash(path, n) for n in os.listdir(path)]
        if args.a:
            ns = [".\\", "..\\"] + ns
            if re.match('^[a-z]:[\\\\/]$', path, re.IGNORECASE):
                ns.pop(1)

        if args.one or not isatty or args.l:
            if args.l:
                text = "{:>19} {:>16} {}".format("mtime","size","path")
                print_utf8(text)
                for n in ns:
                    fullname = os.path.join(path, trimslash(n))
                    mdate = getmtime(fullname).strftime("%Y-%m-%d %H:%M:%S")
                    size = getsize(fullname)
                    text = "{} {:>16} {}".format(mdate, size, n)
                    print_utf8(text)
            else:
                for n in ns:
                    print_utf8(n)
        else:
            terminal_size = shutil.get_terminal_size((80, 20))
            columns = terminal_size.columns
            
            nsl = [len(n) for n in ns]
            nsl.sort()
            
            nmax = nsl.pop()
            nsl.insert(0, nmax)

            cols = 0
            avail = columns
            for l in nsl:
                avail -= l + 2
                cols += 1
                if avail < 0:
                    cols -= 1
                    break
            
            if cols < 1:
                cols = 1

            while True:
                rows = int(math.ceil(len(ns) / cols))
                grid, ls, lss = make_grid(ns, cols, rows)
                #debug_print(grid, ls, lss)
                #debug_print("cols", cols, "lss", lss)
                if lss < columns or cols == 1:
                    print_grid(grid, ls)
                    break
                cols -= 1
        if header:
            print_utf8("")
    
if __name__ == "__main__":
    main()