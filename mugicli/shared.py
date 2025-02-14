from subprocess import Popen, PIPE
import glob
import sys
import io
import subprocess
import os
import re
import locale
import datetime
import shutil
import time

NUM_RX = r'([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)'

WIN_BUILTINS = ['echo', 'dir', 'type', 'copy', 'call', 'start']

def split_list(vs, sep):
    res = []
    for v in vs:
        if v == sep:
            yield res
            res = []
        else:
            res.append(v)
    yield res
    res = []

def glob_paths(paths):
    res = []
    for path in paths:
        if has_magic(path):
            res += glob.glob(path)
        else:
            res.append(path)
    return res

def glob_paths(paths):
    return _glob_paths_pred(paths, lambda path: True)

def glob_paths_files(paths):
    return _glob_paths_pred(paths, lambda path: os.path.isfile(path))

def glob_paths_existing_files(paths):
    res = []
    for path in paths:
        if has_magic(path):
            for item in glob.glob(path):
                if os.path.isfile(item):
                    res.append(item)
        else:
            if not os.path.exists(path):
                raise ValueError("path {} does not exist".format(path))
            if os.path.isfile(path):
                res.append(path)
    return res

def glob_paths_dirs(paths):
    return _glob_paths_pred(paths, lambda path: os.path.isdir(path))

def has_magic(path):
    # brackets in path is ambigous
    if os.path.exists(path):
        return False
    return glob.has_magic(path) # ok

def _glob_paths_pred(paths, pred):
    res = []
    for path in paths:
        if has_magic(path):
            for item in glob.glob(path):
                if pred(item):
                    res.append(item)
        else:
            if pred(path):
                res.append(path)
    return res

def glob_paths_dirs(paths):
    res = []
    for path in paths:
        if has_magic(path):
            for item in glob.glob(path):
                if os.path.isdir(item):
                    res.append(item)
        else:
            res.append(path)
    return res

def drop_last_empty_line(lines):
    if lines[-1].strip() == "":
        lines.pop()

"""
def print(arg, encoding='utf-8'):
    if isinstance(arg, bytes):
        print_bytes(arg)
    elif isinstance(arg, list):
        print_lines(arg, encoding)
    elif isinstance(arg, str):
        print_lines([arg], encoding)
"""

def print_bytes(bytes_):
    sys.stdout.buffer.write(bytes_)

def print_lines(lines, encoding='utf-8'):
    for line in lines:
        #sys.stdout.write(line)
        print_bytes(line.encode(encoding))

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def read_bytes(paths):
    if isinstance(paths, list):
        return _read_bytes_many(paths)
    return _read_bytes_one(paths)

def _read_bytes_one(path):
    if path is None:
        return sys.stdin.buffer.read()
    with open(path, 'rb') as f:
        return f.read()

def _read_bytes_many(paths):
    stdin_mode = len(paths) == 0
    if stdin_mode:
        return read_bytes(None)
    else:
        return b''.join([read_bytes(path) for path in paths])

def split_to_lines(text):
    lines = text.split('\n')
    line = lines[-1]
    lines = [line + '\n' for line in lines]
    lines[-1] = line
    return lines

def read_lines(paths, encoding='utf-8', drop_last_empty_line_ = False):
    if isinstance(paths, list):
        return _read_lines_many(paths, encoding, drop_last_empty_line_)
    return _read_lines_one(paths, encoding, drop_last_empty_line_)

def line_reader(paths, from_stdin, encoding='utf-8', drop_last_empty_line_ = False):
    if from_stdin:
        for i, line in enumerate(_read_lines_one(None, encoding, drop_last_empty_line_)):
            yield i, line, '-'
    else:
        for path in paths:
            for i, line in enumerate(_read_lines_one(path, encoding, drop_last_empty_line_)):
                yield i, line, path

def _read_lines_many(paths, encoding='utf-8', drop_last_empty_line_ = False):
    stdin_mode = len(paths) == 0
    if stdin_mode:
        return _read_lines_one(None, encoding, drop_last_empty_line_)
    lines = []
    for path in paths:
        lines += _read_lines_one(path, encoding, drop_last_empty_line_)
    return lines

def _read_lines_one(path, encoding='utf-8', drop_last_empty_line_ = False):
    bytes_ = read_bytes(path)
    lines = split_to_lines(bytes_.decode(encoding))
    if drop_last_empty_line_ and lines[-1] in ['\r', '']:
        lines.pop()
    return lines

def read_lines_(paths, drop_last_empty_line_ = False):
    lines = []

    stdin_mode = len(paths) == 0

    if stdin_mode:
        lines = list(sys.stdin)
        if drop_last_empty_line_:
            drop_last_empty_line(lines)
    else:
        for path in paths:
            with open(path, 'r', encoding='utf-8') as f:
                lines_ = f.readlines()
            if drop_last_empty_line_:
                drop_last_empty_line(lines_)
            lines += lines_

    return lines

def is_executable(cmd0):
    if cmd0 in WIN_BUILTINS:
        return True
    if '\\' in cmd0 or '/' in cmd0:
        return os.path.exists(cmd0)
    return shutil.which(cmd0) is not None

def adjust_command(cmd):
    if sys.platform == 'win32':
        if cmd[0] in WIN_BUILTINS or re.match("^echo.$", cmd[0]):
            return ['cmd','/c'] + cmd
    return cmd

def cmd_join(cmd):
    res = []
    for e in cmd:
        if ' ' in e:
            e = '"{}"'.format(e)
        res.append(e)
    return " ".join(res)

def run(cmd, cwd = None, verbose=False, print_date=False, print_time=False, end = '\n'):
    orig_cmd = cmd
    cmd = adjust_command(cmd)
    if print_date or print_time:
        now = datetime.datetime.now()
    if print_date:
        print(now.strftime('%Y-%m-%d'), end=end, file=sys.stderr)
    if print_time:
        print(now.strftime('%H:%M:%S'), end=end, file=sys.stderr)
    if verbose:
        print(cmd_join(orig_cmd), end=end, file=sys.stderr)
    if print_date or print_time or verbose:
        print(flush=True, file=sys.stderr)
    t1 = time.time()
    proc = subprocess.run(cmd, cwd=cwd)
    t2 = time.time()
    return proc, t2 - t1

def index_of_int(args):
    for i, arg in enumerate(args):
        if re.match('^-[0-9]+$', arg):
            return i

def parse_args(short, long, short_val, long_val, args):
    opts = {k: False for k in short + long}
    for n in short_val + long_val:
        opts[n] = None
    while len(args) > 0:
        arg = args[0]
        if arg.startswith('--') and arg[2:] in long:
            opts[arg[2:]] = True
        elif arg.startswith('--') and arg[2:] in long_val:
            opts[arg[2:]] = args[1]
            args.pop(0)
        elif arg.startswith('-') and arg[1:] in short_val:
            opts[arg[1:]] = args[1]
            args.pop(0)
        elif arg.startswith('-') and all([c in short for c in arg[1:]]):
            for c in arg[1:]:
                opts[c] = True
        else:
            return opts, args
        args.pop(0)
    return opts, args

def unquote(s):
    if s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s

# set DEBUG_MUGICLI=1
# set DEBUG_MUGICLI=0
# DEBUG_MUGICLI=1
# DEBUG_MUGICLI=0
if os.environ.get('DEBUG_MUGICLI') == "1":
    debug_print = lambda *args, **kwargs: print(*args, **kwargs, file=sys.stderr)
else:
    debug_print = lambda *args, **kwargs: None

loc = locale.getlocale()
if sys.platform == 'win32' and loc == ('Russian_Russia', '1251'):
    stdout_codec = 'cp866'
else:
    stdout_codec = loc[1]