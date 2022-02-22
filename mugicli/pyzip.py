import os
import argparse
import zipfile
from .shared import print_utf8

def main():
    parser = argparse.ArgumentParser(description='appends, extracts and list contents of zip archive')
    parser.add_argument('command', choices=['a','x','l'])
    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('zip')
    parser.add_argument('sources', nargs='*') # todo wildcards
    args = parser.parse_args()

    dst_base = args.output if args.output is not None else os.getcwd()

    if args.command == 'a':
        raise Exception("Not implemented")

    if args.command == 'x':
        with zipfile.ZipFile(args.zip) as zf:
            for name in zf.namelist():
                name_ = name.replace('/','\\')
                if len(args.sources) == 0 or name in args.sources or name_ in args.sources:
                    #dest = os.path.join(dst_base, name)
                    print("extract {} to {}".format(name, dst_base))
                    zf.extract(name, dst_base)
    if args.command == 'l':
        with zipfile.ZipFile(args.zip) as zf:
            for name in zf.namelist():
                print_utf8(name + "\n")

if __name__ == "__main__":
    main()