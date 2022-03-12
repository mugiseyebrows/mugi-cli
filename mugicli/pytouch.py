import argparse
from datetime import date
import datetime
import dateutil.parser
import glob
import os
from .shared import eprint, has_magic
from . import parse_time_arg

def set_mtime(filename, mtime):
    stat = os.stat(filename)
    atime = stat.st_atime
    os.utime(filename, times=(atime, mtime.timestamp()))

def main():
    parser = argparse.ArgumentParser(description='changes mtime to current time or specified time')
    parser.add_argument('path', nargs='+', help='target path')
    parser.add_argument('-d', help='datetime or relative time in format [+-]NUM[d|h|m|s] format')

    args = parser.parse_args()

    if args.d:
        d = parse_time_arg(args.d)
        if d is not None:
            now = datetime.datetime.now()
            mtime = now + datetime.timedelta(seconds=d)
        else:
            mtime = dateutil.parser.parse(args.d)
    else:
        mtime = datetime.datetime.now()

    for path in args.path:
        if has_magic(path):
            paths = glob.glob(path)
        else:
            paths = [path]
        for path_ in paths:
            try:
                if os.path.exists(path_):
                    set_mtime(path_, mtime)
                else:
                    with open(path_, 'w') as f:
                        pass
            except Exception as e:
                eprint(e)

if __name__ == "__main__":
    main()