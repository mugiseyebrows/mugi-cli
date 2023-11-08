import re
import os
import sys
from .shared import parse_args
from bashrange import expand_args
from dataclasses import dataclass
from . import print_utf8
from .shared import debug_print

def print_help():
    print("""usage: pyecho [-e] [-n] [--stdout] [args...] [--stderr] [args...]

prints text to stdout and stderr

options:
  -h --help  show this message and exit
  -e         decode escape sequences
  -n         do not print newline
  --stdout   print following args to stdout
  --stderr   print following args to stderr

examples:
  pyecho hello world
  pyecho -e "1\\n2\\n3"
  pyecho -n test
  pyecho {1..5}
  pyecho this goes to stdout --stderr this goes to stderr
""")

@dataclass
class Opts:
    newline: bool = False
    help: bool = False
    escape: bool = False

def parse_opts(args):
    opts = Opts()
    for i, arg in enumerate(args):
        if arg in ['-n', '--newline']:
            opts.newline = True
        elif arg in ['-h', '--help']:
            opts.help = True
        elif arg in ['-e', '--escape']:
            opts.escape = True
        else:
            return opts, args[i:]
    return opts, []

def to_stdout_stderr(args):
    stdout = []
    stderr = []
    dst = stdout
    for arg in args:
        if arg == '--stdout':
            dst = stdout
        elif arg == '--stderr':
            dst = stderr
        else:
            dst.append(arg)
    return stdout, stderr

def main():

    def unescape(arg):
        return arg.encode('utf-8').decode('unicode_escape')

    args = expand_args()
    debug_print("expanded", args)
    opts, args = parse_opts(args)
    debug_print("opts", opts, "args", args)
    stdout, stderr = to_stdout_stderr(args)
    debug_print("stdout", stdout, "stderr", stderr)

    if opts.help:
        print_help()
        return
    
    if opts.escape:
        transform = lambda args: [unescape(arg) for arg in args]
    else:
        transform = lambda args: args

    if len(stdout) > 0:
        text = " ".join(transform(stdout))
        end = b'' if opts.newline else b'\n'
        print_utf8(text, end)
    if len(stderr) > 0:
        text = " ".join(transform(stderr))
        end = b'' if opts.newline else b'\n'
        print_utf8(text, end, file=sys.stderr)

if __name__ == "__main__":
    main()