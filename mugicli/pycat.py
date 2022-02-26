import argparse
from datetime import date
import datetime
import dateutil.parser
import glob
import os
import sys
from .shared import glob_paths, eprint

def main():
    parser = argparse.ArgumentParser(description='prints file to stdout')
    parser.add_argument('path', nargs='+')
    parser.add_argument('--text', '-t', action='store_true')

    args = parser.parse_args()

    paths = glob_paths(args.path)

    for path in paths:
        try:
            with open(path, 'rb') as f:
                sys.stdout.buffer.write(f.read())
        except Exception as e:
            eprint(e)

if __name__ == "__main__":
    main()