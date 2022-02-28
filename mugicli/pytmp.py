import argparse
import sys
import re
import json
import tempfile
import os
import shutil
from .shared import print_bytes
import textwrap

# todo clean
# todo env PYTMP_DIR

def pytmp_path():
    return os.path.join(os.path.expanduser('~'), '.pytmp')

def write_pathmap(pathmap):
    with open(pytmp_path(), 'w', encoding='utf-8') as f:
        json.dump(pathmap, f, ensure_ascii=False, indent=1)

def read_pathmap():
    try:
        with open(pytmp_path(), encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return dict()

def main():

    epilog = textwrap.dedent("""\
    examples:
        pyecho -e 3\\n1\\n2 | pytmp -o foo
        pytmp -i foo | pysort
        pytmp -p foo | pyxargs pycat 
    """)

    parser = argparse.ArgumentParser(description='temporary file helper', epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--print', nargs='+', help='print filenames')
    parser.add_argument('-i', '--input', nargs='+', help='input data from file')
    parser.add_argument('-o', '--output', help='output data to file')
    parser.add_argument('--suffix', default='.tmp')

    args = parser.parse_args()

    pathmap = read_pathmap()

    if args.output:
        fd, path = tempfile.mkstemp(prefix=args.output + '-', suffix=args.suffix)
        with open(path, 'wb') as f:
            f.write(sys.stdin.buffer.read())
        os.close(fd)
        pathmap[args.output] = path
        write_pathmap(pathmap)
    elif args.input is not None:
        for n in args.input:
            path = pathmap[n]
            with open(path, 'rb') as f:
                print_bytes(f.read())

    if args.print is not None:
        for n in args.print:
            path = pathmap[n]
            print(path)

if __name__ == "__main__":
    main()