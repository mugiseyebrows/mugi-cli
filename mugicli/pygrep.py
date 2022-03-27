from mugicli import read_file_lines, read_stdin_lines
from .shared import glob_paths_files, line_reader, print_lines, has_magic, print_utf8
import sys
import argparse
import re
import glob

# todo binary files

def main():
    
    parser = argparse.ArgumentParser(add_help=False, description='prints matching lines')
    parser.add_argument('expr')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='ignore case')
    parser.add_argument('-o', '--only-matching', action='store_true')
    parser.add_argument('-v', '--invert-match', action='store_true', help='select non-matching lines')
    parser.add_argument('-H', '--with-filename', action='store_true', help='print file name')
    parser.add_argument('-h', '--without-filename', action='store_true', help='do not print file name')
    parser.add_argument('-n', '--line-number', action='store_true', help='print line number')
    parser.add_argument('--help', action='help')
    parser.add_argument('path', nargs='*')

    args = parser.parse_args()

    if args.with_filename:
        print_filename = True
    elif args.without_filename:
        print_filename = False
    else:
        many_inputs = len(args.path) > 1 or (len(args.path) > 0 and has_magic(args.path[0]))
        print_filename = many_inputs

    flags = re.IGNORECASE if args.ignore_case else 0
    rx = re.compile(args.expr, flags)

    def formatter(path, i, m, line):
        cols = []
        if print_filename:
            cols.append(path)
        if args.line_number:
            cols.append(str(i+1))
        if args.only_matching:
            cols.append(m.group(0))
        else:
            cols.append(line)
        return ':'.join(cols)

    def pred_match(line):
        m = rx.search(line)
        return m, m is not None

    def pred_not_match(line):
        m = rx.search(line)
        return m, m is None

    if args.invert_match:
        pred = pred_not_match
    else:
        pred = pred_match

    def on_line(path, i, line):
        m, matched = pred(line)
        if matched:
            #print_lines([])
            print_utf8(formatter(path, i, m, line))

    if len(args.path) == 0:
        lines = read_stdin_lines(drop_last=True, rstrip=True)
        for i, line in enumerate(lines):
            on_line('-', i, line)
    else:
        for path in glob_paths_files(args.path):
            lines = read_file_lines(path, drop_last=True, rstrip=True)
            for i, line in enumerate(lines):
                on_line(path, i, line)

if __name__ == "__main__":
    main()
    