import sys
import re
from .shared import glob_paths, glob_paths_files, read_bytes, print_bytes
import argparse
import hashlib

def read_stdin_text():
    data = sys.stdin.buffer.read()
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        text = data.decode(sys.stdin.encoding)
    return text

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
    
