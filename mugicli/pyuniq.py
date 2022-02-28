import argparse
from random import uniform
from collections import defaultdict
from .shared import glob_paths_files, read_lines, print_lines

def main():
    parser = argparse.ArgumentParser(description='prints unique or nonunique lines from sorted array of lines')
    parser.add_argument('--count', '-c', action='store_true')
    parser.add_argument('--repeated','-d',action='store_true')
    parser.add_argument('--unique','-u',action='store_true')
    parser.add_argument('path', nargs="*")

    args = parser.parse_args()
    paths = glob_paths_files(args.path)
    lines = read_lines(paths)

    stat = defaultdict(lambda: 0)
    for line in lines:
        stat[line] += 1
    
    if args.repeated:
        lines_ = [line for line in lines if stat[line] > 1]
    elif args.unique:
        lines_ = [line for line in lines if stat[line] == 1]
    else:
        lines_ = lines

    res = [lines_[0]]
    for line in lines_:
        if res[-1] != line:
            res.append(line)

    if args.count:
        formatter = lambda line: "{:5d} {}".format(stat[line], line)
    else:
        formatter = lambda line: line

    lines_ = [formatter(line) for line in res]
    print_lines(lines_)

if __name__ == "__main__":
    main()