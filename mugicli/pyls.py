import argparse
from .shared import glob_paths, print_utf8, has_magic
import glob
import os

def main():
    parser = argparse.ArgumentParser(description='lists directory')
    parser.add_argument('path', nargs='*')
    args = parser.parse_args()

    if len(args.path) == 0:
        paths = ['.']
    else:
        paths = args.path

    for path in paths:
        if has_magic(path):
            for f in glob.glob(path):
                print_utf8(f)
        else:
            if len(paths) > 1:
                print_utf8(path + ":")
            for root, dirs, files in os.walk(path):
                for d in dirs:
                    print_utf8(d + "/")
                for f in files:
                    print_utf8(f)
                while len(dirs) > 0:
                    dirs.pop()
    

if __name__ == "__main__":
    main()