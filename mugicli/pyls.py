import argparse
from .shared import glob_paths, has_magic
import glob
import os
import sys
from . import chunks, print_utf8
import math
from itertools import count

def tabulate(lens, rows, columns):
    data = []
    sizes = []
    for chunk in chunks(lens, rows):
        size = max(chunk) + 1
        sizes.append(size)
        data.append(chunk)
        if sum(sizes) > columns:
            return False, []
    if sum(sizes) > columns:
        return False, []
    return True, sizes
    
def print_group(items, isatty):
    if isatty:
        lens = [len(item) for item in items]
        area = sum(lens)
        columns = os.get_terminal_size().columns
        rows = int(math.ceil(area / columns))
        if max(lens) + 1 >= columns:
            for line in items:
                print_utf8(line)
            return
        while True:
            ok, sizes = tabulate(lens, rows, columns)
            if ok:
                lines = ["" for _ in range(rows)]
                for chunk, size in zip(chunks(items, rows), sizes):
                    for j, item in enumerate(chunk):
                        lines[j] = lines[j] + str.ljust(item, size)
                for line in lines:
                    print_utf8(line)
                return
            rows += 1
    else:
        for item in items:
            print_utf8(item)

def main():
    parser = argparse.ArgumentParser(description='lists directory')
    parser.add_argument('path', nargs='*')
    args = parser.parse_args()

    if len(args.path) == 0:
        paths = ['.']
    else:
        paths = args.path

    isatty = sys.stdout.isatty()

    for path in paths:
        if has_magic(path):
            print_group(list(glob.glob(path)), isatty)
        else:
            if len(paths) > 1:
                print_utf8(path + ":")
            for root, dirs, files in os.walk(path):
                print_group([d + "/" for d in dirs] + files, isatty)
                while len(dirs) > 0:
                    dirs.pop()
    
if __name__ == "__main__":
    main()