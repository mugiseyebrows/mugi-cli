import argparse
import sys
from .shared import glob_paths_files, eprint
from . import chunks, parse_size, print_utf8

def print_hex(data, seek):
    for i, chunk in enumerate(chunks(data, 16)):
        print_utf8("{:08x}".format(i * 16 + seek), end=' ')
        chars = ["{:02x}".format(c) for c in chunk] + ["  " for _ in range(len(chunk), 16)]
        print_utf8(" ".join(chars), end='  ')
        text = chunk.decode('utf-8', errors='replace').replace('\n', '.').replace('\r','.')
        print_utf8(text)

def seek_and_read(f, seek, len_):
    f.seek(seek)
    size = len_ if len_ > -1 else None
    data = f.read(size)
    return data

def main():
    parser = argparse.ArgumentParser(description='prints file as hex')
    parser.add_argument('path', nargs='*')
    parser.add_argument('-s','--seek', help='start at offset')
    parser.add_argument('-l','--len', help='number of bytes to print')

    args = parser.parse_args()

    if args.seek is None:
        seek = 0
    else:
        seek = parse_size(args.seek)

    if args.len is None:
        len_ = -1
    else:
        len_ = parse_size(args.len)

    if len(args.path) == 0:
        data = seek_and_read(sys.stdin.buffer, seek, len_)
        print_hex(data, seek)
    else:
        for path in glob_paths_files(args.path):
            try:
                with open(path, 'rb') as f:
                    data = seek_and_read(f, seek, len_)
                print_hex(data, seek)
            except Exception as e:
                eprint(e)

if __name__ == "__main__":
    main()