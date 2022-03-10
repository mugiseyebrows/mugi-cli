import os
import argparse
import zipfile
from zipfile import ZIP_STORED, ZIP_DEFLATED, ZIP_BZIP2, ZIP_LZMA
from .shared import print_utf8, glob_paths
import sys

def main():

    COMPRESSION_METHODS = {
        'deflate': ZIP_DEFLATED,
        'd': ZIP_DEFLATED,
        'lzma': ZIP_LZMA,
        'l': ZIP_LZMA,
        'bzip2': ZIP_BZIP2,
        'b': ZIP_BZIP2,
        'store': ZIP_STORED,
        's': ZIP_STORED
    }

    parser = argparse.ArgumentParser(description='appends, extracts and list contents of zip archive')
    parser.add_argument('command', choices=['a','x','l'], help='add extract list')
    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('-m', choices=list(COMPRESSION_METHODS.keys()), help='compression method')
    parser.add_argument('-l', type=int, help="compression level 0..9 for deflate (0 - best speed, 9 - best compression) 1..9 for bzip2, has no effect if method is store or lzma")
    parser.add_argument('--base', help='base directory')
    parser.add_argument('zip')
    parser.add_argument('sources', nargs='*') # todo wildcards
    args = parser.parse_args()

    dst_base = args.output if args.output is not None else os.getcwd()

    compresslevel = args.l

    if args.command == 'a':
        paths = glob_paths(args.sources)
        compression = COMPRESSION_METHODS[args.m] if args.m is not None else ZIP_DEFLATED
        with zipfile.ZipFile(args.zip, 'a', compression=compression, compresslevel=compresslevel) as zf:
            for path in paths:
                if args.base is None:
                    if os.path.isabs(path):
                        base = os.path.dirname(path)
                    else:
                        base = os.getcwd()
                else:
                    base = args.base
                for root, dirs, files in os.walk(path):
                    for f in files:
                        p = os.path.join(root, f)
                        relpath = os.path.relpath(p, base)
                        zf.write(p, relpath)
                        
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
                print_utf8(name)

if __name__ == "__main__":
    main()