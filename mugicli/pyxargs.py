import sys
import re
import subprocess
from .shared import eprint, run, parse_args
from . import read_stdin_text, chunks
import textwrap

def read_stdin_args():
    text = read_stdin_text()
    args = [line for line in [line.strip() for line in text.split('\n')] if line != '']
    return args

def is_int(s):
    try:
        int(s)
        return True
    except Exception as e:
        pass
    return False

def print_help():
    print(textwrap.dedent("""\
    usage: pyxargs [-n num] command [args...]

    reads arguments from stdin and applies them to command

    optional arguments:
    -h --help  show this message and exit
    -n         split arguments to chunks of n
    """))

def main():
    opts, args1 = parse_args(['h'],['help'],['n'],[], sys.argv[1:])
    if opts['h'] or opts['help']:
        print_help()
        return
    args2 = read_stdin_args()
    if opts['n'] is None:
        run(args1 + args2)
    else:
        for args in chunks(args2, int(opts['n'])):
            run(args1 + args)

if __name__ == "__main__":
    main()