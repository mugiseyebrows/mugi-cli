import sys
import re
from .shared import glob_paths, glob_paths_files, read_bytes, print_bytes
import argparse
import hashlib
import argparse
import sys
from .shared import glob_paths_files, print_utf8, drop_last_empty_line, index_of_int

def decode_bytes(data):
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        text = data.decode(sys.stdin.encoding)
    return text

def read_file_bin(path):
    with open(path, 'rb') as f:
        return f.read()

def read_stdin_bin():
    return sys.stdin.buffer.read()

def read_stdin_text():
    data = sys.stdin.buffer.read()
    return decode_bytes(data)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def parse_size(arg):
    m = re.match('^([-+]?[0-9.e]+)+([cwbkmg]?)$', arg, re.IGNORECASE)
    if m is None:
        return None
    size = float(m.group(1))
    prefix = m.group(2)
    return int(size * {'k': 1024, 'm': 1024 * 1024, 'g': 1024 * 1024 * 1024, 'c': 1, 'b': 512, '': 1}[prefix.lower()])

import argparse

(
    TO_UNIX,
    TO_DOS
) = range(2)

def convertlineterm(to_what):

    description = {
        TO_UNIX: 'converts line endings from dos to unix (\\r\\n -> \\n)',
        TO_DOS: 'converts line endings from unix to dos (\\n -> \\r\\n)'
    }[to_what]

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('path', nargs='*')
    args = parser.parse_args()
    paths = glob_paths_files(args.path)

    stdin_mode = len(args.path) == 0

    if to_what == TO_UNIX:
        subj = b'\r\n'
        repl = b'\n'
    else:
        subj = b'\n'
        repl = b'\r\n'

    if stdin_mode:
        bytes_ = read_bytes(None)
        print_bytes(bytes_.replace(subj, repl))
    else:
        for path in paths:
            bytes_ = read_bytes(path)
            with open(path, 'wb') as f:
                f.write(bytes_.replace(subj, repl))


def files_hash(paths, from_stdin, alg):
    if from_stdin:
        hash = hashlib.new(alg)
        hash.update(sys.stdin.buffer.read())
        print(" ".join([hash.hexdigest(), "-"]))
    else:
        for path in paths:
            with open(path, 'rb') as f:
                hash = hashlib.new(alg)
                hash.update(f.read())
                print(" ".join([hash.hexdigest(), path]))

def files_hash_main(alg):
    parser = argparse.ArgumentParser(description='prints {} hashsum of file'.format(alg))
    parser.add_argument('path', nargs='*')
    args = parser.parse_args()
    from_stdin = len(args.path) == 0
    paths = glob_paths_files(args.path)
    files_hash(paths, from_stdin, alg)
    
(
    T_HEAD,
    T_TAIL
) = range(2)

def print_lines_utf8(lines):
    for line in lines:
        print_utf8(line, end='')

def head_tail_print_lines(lines, n, t):
    if t == T_HEAD:
        print_lines_utf8(lines[:n])
    else:
        print_lines_utf8(lines[-n:])

def bytes_to_lines(data):
    text = decode_bytes(data)
    lines = [line + '\n' for line in text.split('\n')]
    drop_last_empty_line(lines)
    return lines

def head_tail_main(t):

    args_ = sys.argv[1:]

    while True:
        i = index_of_int(args_)
        #print(i)
        if i is None:
            break
        args_ = args_[:i] + ['-n', str(abs(int(args_[i])))] + args_[i+1:]

    description = 'prints n lines from {} of file'.format('head' if t == T_HEAD else 'tail')

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-n', type=int, default=10, help='number of lines to print')
    parser.add_argument('path', nargs="*")
    args = parser.parse_args(args_)
    
    if len(args.path) == 0:
        data = read_stdin_bin()
        lines = bytes_to_lines(data)
        head_tail_print_lines(lines, args.n, t)
    else:
        paths = glob_paths_files(args.path)
        for path in paths:
            data = read_file_bin(path)
            lines = bytes_to_lines(data)
            head_tail_print_lines(lines, args.n, t)

def parse_time_arg(text):
    m = re.match('([+-]?)([0-9.e-]+)(d|h|m|s|)', text)
    if m is None:
        return
    sign = -1 if m.group(1) == '-' else 1
    value = float(m.group(2))
    suffix = m.group(3)
    mul = {"d": 3600 * 24, "h": 3600, "m": 60, "s": 1, "": 1}[suffix]
    return sign * mul * value