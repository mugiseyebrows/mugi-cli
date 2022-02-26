import os
import argparse
from .shared import glob_paths, print_utf8
from . import read_stdin_text
import datetime

def print_mtime(path):
    try:
        print_utf8("{} {}".format(datetime.datetime.fromtimestamp(os.path.getmtime(path)), path))
    except Exception as e:
        pass

def main():
    parser = argparse.ArgumentParser(description='prints mtime of file')
    parser.add_argument('path', nargs='*')
    args = parser.parse_args()
    
    if len(args.path) == 0:
        for line in read_stdin_text().split('\n'):
            print_mtime(line.rstrip())
    else:
        paths = glob_paths(args.path)
        for path in paths:
            print_mtime(path)

if __name__ == "__main__":
    main()