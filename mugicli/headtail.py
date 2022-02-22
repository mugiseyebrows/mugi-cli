import argparse
import sys
from .shared import glob_paths, read_bytes, print_lines, drop_last_empty_line, index_of_int
import re

def _print_lines(lines, n, is_head):
    if is_head:
        print_lines(lines[:n])
    else:
        print_lines(lines[-n:])

def bytes_to_lines(bytes_):
    lines = [line + '\n' for line in bytes_.decode('utf-8').split('\n')]
    drop_last_empty_line(lines)
    return lines

def head_tail(is_head = True):

    args_ = sys.argv[1:]

    while True:
        i = index_of_int(args_)
        #print(i)
        if i is None:
            break
        args_ = args_[:i] + ['-n', str(abs(int(args_[i])))] + args_[i+1:]

    description = 'prints n lines from {} of file'.format('head' if is_head else 'tail')

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-n', type=int, default=10, help='number of lines to print')
    parser.add_argument('path', nargs="*")
    args = parser.parse_args(args_)
    paths = glob_paths(args.path)
    stdin_mode = len(paths) == 0

    if stdin_mode:
        bytes_ = read_bytes([])
        lines = bytes_to_lines(bytes_)
        _print_lines(lines, args.n, is_head)
    else:
        for path in paths:
            bytes_ = read_bytes([path])
            lines = bytes_to_lines(bytes_)
            _print_lines(lines, args.n, is_head)