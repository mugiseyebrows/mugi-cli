import os
import argparse
from . import read_file_text, read_stdin_text, print_utf8
from .shared import glob_paths_files
import re
from bashrange import expand_args

def print_cols(line, col_numbers):
    cols = re.split('\\s+', line)
    cols_ = [cols[i-1] if i-1 < len(cols) else '' for i in col_numbers]
    print_utf8(" ".join(cols_))

def main():
    parser = argparse.ArgumentParser(description='extracts and prints specific columns') # todo separators
    parser.add_argument('path', nargs='*')
    parser.add_argument('-n', type=int, nargs='+', help='column number') # todo range expr
    args = parser.parse_args(expand_args())
    if len(args.path) == 0:
        for line in read_stdin_text().split('\n'):
            print_cols(line, args.n)
    else:
        for path in glob_paths_files(args.path):
            text = read_file_text(path)
            for line in text.split("\n"):
                print_cols(line, args.n)

if __name__ == "__main__":
    main()
