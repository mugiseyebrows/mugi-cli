import argparse
import re
from .shared import glob_paths_files, read_bytes, debug_print
from . import read_file_lines, read_stdin_lines, read_stdin_bin
from bashrange import expand_args
import os

(
    MODE_STDIN,
    MODE_XARGS,
    MODE_FILE,
    MODE_PATHS
) = range(4)

def main():

    description='calculates number or lines words, chars and bytes in files'
    epilog="""examples:
  pywc -l text.txt
  pyfind -iname *.txt | pywc -l --input-stdin
"""

    parser = argparse.ArgumentParser(epilog=epilog, description=description, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-l', action='store_true', help='print the newline counts')
    parser.add_argument('-w', action='store_true', help='print the word counts')
    parser.add_argument('-m', action='store_true', help='print the character counts')
    parser.add_argument('-c', action='store_true', help='print the byte counts')
    parser.add_argument('--input', '-i', help='read file paths from file')
    parser.add_argument('-X', '--xargs', action='store_true', help='read file paths from stdin')
    parser.add_argument('path', nargs="*", help="files")

    args = parser.parse_args(expand_args())

    #print(args); exit(0)

    filesize_mode = False
    if [args.l, args.w, args.m, args.c] == [False, False, False, True]:
        filesize_mode = True

    def count_lines(data, path, res):
        c = 0
        m = 0
        w = 0
        l = 0
        if filesize_mode:
            #debug_print("os.path.getsize {}".format(path))
            c = os.path.getsize(path)
        else:
            #debug_print("read {}".format(path))
            text = ''
            try:
                text = data.decode('utf-8')
            except Exception as e:
                print(e)
            c = len(data)
            m = len(text)
            w = len(re.split('\\s+',text.strip()))
            l = len(text.split('\n')) - 1
        res.append((l, w, m, c, path))

    res = []

    mode = MODE_PATHS

    if args.xargs:
        mode = MODE_XARGS
    elif args.input is not None:
        mode = MODE_FILE
    else:
        mode = MODE_PATHS

    if mode == MODE_PATHS and len(args.path) == 0:
        mode = MODE_STDIN

    if mode == MODE_XARGS:
        paths = read_stdin_lines(drop_last=True, rstrip=True)
    elif mode == MODE_FILE:
        paths = read_file_lines(args.input, drop_last=True, rstrip=True)
    elif mode == MODE_PATHS:
        paths = glob_paths_files(args.path)

    if mode == MODE_STDIN:
        data = read_stdin_bin()
        count_lines(data, '-', res)
    else:
        for path in paths:
            count_lines(read_bytes(path), path, res)

    lt = sum([e[0] for e in res])
    wt = sum([e[1] for e in res])
    mt = sum([e[2] for e in res])
    ct = sum([e[3] for e in res])

    lw = max(len(str(lt)), 3)
    ww = max(len(str(wt)), 3)
    mw = max(len(str(mt)), 3)
    cw = max(len(str(ct)), 3)

    if len(res) > 1:
        res.append((lt,wt,mt,ct,'total'))

    pred = [args.l, args.w, args.m, args.c, True]
    if count_true(pred) == 1:
        pred = [True, True, True, True, True]

    fmt = " ".join(['{:' + str(lw) + 'd}' if pred[0] else ''] +
        ['{:' + str(ww) + 'd}' if pred[1] else ''] +
        ['{:' + str(mw) + 'd}' if pred[2] else ''] +
        ['{:' + str(cw) + 'd}' if pred[3] else ''] +
        ['{}'])

    for item in res:
        cols = [v for v, en in zip(item, pred) if en]
        print(fmt.format(*cols))

def count_true(items):
    return len([v for v in items if v])

if __name__ == "__main__":
    main()