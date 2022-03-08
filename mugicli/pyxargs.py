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
    usage: pyxargs [-L NUM] [-I VAR] command [args...]

    reads arguments from stdin and applies them to command

    optional arguments:
      -h --help  show this message and exit
      -L NUM     split arguments to chunks of N args
      -I VAR     replace VAR with arg (assumes -L 1)

    """))

def main():
    opts, args1 = parse_args(['h'],['help'],['L','I'],[], sys.argv[1:])
    if opts['h'] or opts['help']:
        print_help()
        return
    args2 = read_stdin_args()

    if opts['L'] is not None:
        for args in chunks(args2, int(opts['n'])):
            run(args1 + args)
    elif opts['I'] is not None:
        for arg in args2:
            cmd = [a.replace(opts['I'], arg) for a in args1]
            run(cmd)
    else:
        run(args1 + args2)

if __name__ == "__main__":
    main()