from . import read_stdin_lines, print_utf8, read_file_bin, bytes_to_lines
from .shared import glob_paths_existing_files
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=1)
    parser.add_argument("path", nargs="*")    
    args = parser.parse_args()
    #print(args); exit(0)
    if len(args.path) == 0:
        lines = read_stdin_lines(rstrip=False)
        for i, line in enumerate(lines):
            if ((i + 1) % args.n) == 0:
                print_utf8(line, end=b'')
    else:
        i = 0
        for path in glob_paths_existing_files(args.path):
            data = read_file_bin(path)
            lines = bytes_to_lines(data)
            for line in lines:
                if ((i + 1) % args.n) == 0:
                    print_utf8(line, end=b'')
                i += 1

if __name__ == "__main__":
    main()