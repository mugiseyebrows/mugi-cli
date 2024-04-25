import sys
import re
from .shared import glob_paths, glob_paths_files, read_bytes, print_bytes
import argparse
import hashlib
import argparse
import sys
from .shared import glob_paths_files, drop_last_empty_line, index_of_int, stdout_codec
import os
import fnmatch
from bashrange import expand_args

class IsUnicode:
    def __init__(self, value = False):
        self.value = value

    def set(self, value):
        self.value = value

def decode_bytes(data, is_unicode = None):
    try:
        text = data.decode('utf-8')
        if is_unicode:
            is_unicode.set(True)
    except UnicodeDecodeError:
        text = data.decode(stdout_codec)
        if is_unicode:
            is_unicode.set(False)
    return text

def read_file_bin(path):
    with open(path, 'rb') as f:
        return f.read()

def read_stdin_bin():
    return sys.stdin.buffer.read()

def write_stdout_bin(data):
    sys.stdout.buffer.write(data)

def read_stdin_text(is_unicode = None):
    data = sys.stdin.buffer.read()
    return decode_bytes(data, is_unicode)

def read_stdin_lines(drop_last = True, rstrip = True):
    if rstrip:
        lines = [line.rstrip('\r') for line in read_stdin_text().split('\n')]
    else:
        lines = [line + '\n' for line in read_stdin_text().split('\n')]
    if drop_last and lines[-1] in ['\n', '\r\n', '']:
        lines.pop()
    return lines

def read_file_lines(path, drop_last = True, rstrip = True):
    text = read_file_text(path)
    if rstrip:
        lines = [line.rstrip('\r') for line in text.split('\n')]
    else:
        lines = [line + '\n' for line in text.split('\n')]
    if drop_last and lines[-1] in ['\n', '\r\n', '']:
        lines.pop()
    return lines

def read_file_text(path):
    data = read_file_bin(path)
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
    args = parser.parse_args(expand_args())
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
    args = parser.parse_args(expand_args())
    from_stdin = len(args.path) == 0
    paths = glob_paths_files(args.path)
    files_hash(paths, from_stdin, alg)
    
def print_lines_utf8(lines):
    for line in lines:
        print_utf8(line, end='')

def bytes_to_lines(data):
    text = decode_bytes(data)
    lines = [line + '\n' for line in text.split('\n')]
    drop_last_empty_line(lines)
    return lines

# todo bytes, chars

def parse_time_arg(text):
    m = re.match('([+-]?)([0-9.e-]+)(d|h|m|s|)', text)
    if m is None:
        return
    sign = -1 if m.group(1) == '-' else 1
    value = float(m.group(2))
    suffix = m.group(3)
    mul = {"d": 3600 * 24, "h": 3600, "m": 60, "s": 1, "": 1}[suffix]
    return sign * mul * value

def include_exclude(include, exclude, name):
    if include is None and exclude is None:
        return True
    if include is None:
        ok = True
    else:
        ok = False
        for pat in include:
            if fnmatch.fnmatch(name, pat):
                ok = True
    if not ok:
        return False
    if exclude is None:
        return True
    else:
        for pat in exclude:
            if fnmatch.fnmatch(name, pat):
                return False
    return True

def leftpad(s, w):
    return ("{:>" + str(w) + "}").format(s)

def format_size(s, w):
    if s > 1024 * 1024 * 1024:
        return leftpad("{:.1f}G".format(s / (1024 * 1024 * 1024)), w)
    elif s > 1024 * 1024:
        return leftpad("{:.1f}M".format(s / (1024 * 1024)), w)
    elif s > 1024:
        return leftpad("{:.1f}K".format(s / (1024)), w)
    return leftpad(str(s), w)

def format_size_g(s, w):
    return leftpad("{:.1f}G".format(s / (1024 * 1024 * 1024)), w)

def print_utf8(s, end=b'\n', file=sys.stdout, flush = False):
    if not isinstance(end, bytes):
        end = end.encode('utf-8')
    file.buffer.write(s.encode('utf-8') + end)
    if flush:
        file.buffer.flush()
