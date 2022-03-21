from ast import parse
import os
import argparse
import zipfile
from zipfile import ZIP_STORED, ZIP_DEFLATED, ZIP_BZIP2, ZIP_LZMA
from .shared import print_utf8, glob_paths
from . import read_file_text
import sys

# todo read from stdin
# todo ouput to stdout

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
    parser.add_argument('command', choices=['a','x','l'], help='add extract list') # todo u - update
    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('-m', choices=list(COMPRESSION_METHODS.keys()), help='compression method')
    parser.add_argument('-l', type=int, help="compression level 0..9 for deflate (0 - best speed, 9 - best compression) 1..9 for bzip2, has no effect if method is store or lzma")
    parser.add_argument('--base', help='base directory')
    parser.add_argument('--dir', help='prepend directory to path')
    parser.add_argument('--list', help='path to list of files')
    parser.add_argument('-s', '--silent', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('zip')
    parser.add_argument('sources', nargs='*')
    args = parser.parse_args()

    dst_base = args.output if args.output is not None else os.getcwd()

    compresslevel = args.l

    if args.verbose and args.silent:
        print_utf8('choose one: verbose or silent')
        exit(1)

    verbose = args.verbose or not args.silent

    if args.command == 'a':
        if args.list is None:
            paths = glob_paths(args.sources)
        else:
            lines = read_file_text(args.list).split('\n')
            paths = [line.rstrip() for line in lines if line.rstrip() != '']

        compression = COMPRESSION_METHODS[args.m] if args.m is not None else ZIP_DEFLATED

        def add_file(zf, p, base):
            relpath = os.path.relpath(p, base)
            if args.dir:
                relpath = os.path.join(args.dir, relpath)
            if verbose:
                print_utf8(p)
            zf.write(p, relpath)

        with zipfile.ZipFile(args.zip, 'a', compression=compression, compresslevel=compresslevel) as zf:
            for path in paths:
                if args.base is None:
                    if os.path.isabs(path):
                        base = os.path.dirname(path)
                    else:
                        base = os.getcwd()
                else:
                    base = args.base

                if os.path.isfile(path):
                    add_file(zf, path, base)
                else:
                    for root, dirs, files in os.walk(path):
                        for f in files:
                            p = os.path.join(root, f)
                            add_file(zf, p, base)
                        
    if args.command == 'x':
        # todo extract globs and dirs, use --list
        with zipfile.ZipFile(args.zip) as zf:
            for name in zf.namelist():
                name_ = name.replace('/','\\')
                if len(args.sources) == 0 or name in args.sources or name_ in args.sources:
                    #dest = os.path.join(dst_base, name)
                    print("extract {} to {}".format(name, dst_base))
                    zf.extract(name, dst_base)
                    
    if args.command == 'l':
        # todo print size
        with zipfile.ZipFile(args.zip) as zf:
            for name in zf.namelist():
                print_utf8(name)

if __name__ == "__main__":
    main()