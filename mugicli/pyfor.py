from bashrange import expand_args

import time
from .shared import run, is_executable
import glob
import itertools
import sys
import re

def print_help():
    print("""
usage: pyfor [-h] [--help] [-n COUNT] [--list items...] [--glob exprs...] [--sleep SECONDS] 
  [--print-time] [-v] [--newline] -- command [args]

optional arguments:
  -n COUNT               run command COUNT times
  --list items...        run command for each item in list
  --glob items...        run command for each path matched by globs
  -s, --sleep SECONDS    sleep SECONDS after command
  --print-date --pd      print current date before executing command
  --print-time --pt      print current time before executing command
  -v, --verbose          print command and separator before executing command
  --newline --nl         print blank line after command output
  --stat --st            print stat

examples:
  pyfor -n 5 echo :iter:
  pyfor -n 1..5 -- echo :iter:
  pyfor -n 10 -s 10 --newline cmd /c "tasklist | pygrep python"
  pyfor -s 60 --print-time pynmap example.com -p 80
  pyfor -s 30 --newline pyfind build -mmin -0.1
  pyfor --list pytrue pyfalse -- cmd /c ":iter: && echo yeah :iter: || echo meh :iter:"

runs command(s) n times or forever
""")

(
    MODE_NONE,
    MODE_N,
    MODE_LIST,
    MODE_GLOB
) = range(4)

def main():
    args = expand_args()
    
    sleep = 0
    verbose = False
    newline = False
    print_date = False
    print_time = False
    items = itertools.count()
    globs = []
    mode = MODE_NONE
    print_stat = False

    i = 0
    while True:
        if args[i] in ['--help', '-h']:
            print_help()
            exit(0)
        elif args[i] in ['-n', '-r', '--range', '-rn']:
            mode = MODE_N
            arg = args[i+1]
            i += 2
            m = re.match('([0-9]+)\\.\\.([0-9]+)\\.\\.([0-9]+)', arg)
            if m:
                v1, v2, v3 = [int(m.group(i)) for i in range(1,4)]
                items = range(v1, v2+1, v3)
                continue
            m = re.match('([0-9]+)\\.\\.([0-9]+)', arg)
            if m:
                v1, v2 = [int(m.group(i)) for i in range(1,3)]
                items = range(v1, v2+1)
                continue
            items = range(int(arg))
        elif args[i] in ['-s', '--sleep', '-sleep']:
            sleep = float(args[i+1])
            i += 2
        elif args[i] in ['-v', '--verbose']:
            verbose = True
            i += 1
        elif args[i] in ['--newline', '--nl', '-nl']:
            newline = True
            i += 1
        elif args[i] in ['--print-time', '--pt', '-pt']:
            print_time = True
            i += 1
        elif args[i] in ['--print-date', '--pd', '-pd']:
            print_date = True
            i += 1
        elif args[i] in ['--stat', '--st', '-st']:
            print_stat = True
            i += 1
        elif args[i] == '--rt':
            rt = True
            i += 1
        elif args[i] == '--list':
            i += 1
            items = []
            while not args[i].startswith('-'):
                items.append(args[i])
                i += 1
        elif args[i] == '--glob':
            i += 1
            while not args[i].startswith('-'):
                globs.append(args[i])
                i += 1
        elif args[i] == '--':
            i += 1
            cmd = args[i:]
            break
        elif args[i].startswith('-'):
            raise ValueError("unrecognized argument {}".format(args[i]))
        else:
            cmd = args[i:]
            if len(cmd) == 0:
                raise ValueError("command is empty")
            break
    
    def repl_iter(cmd, iter):
        res = []
        for e in cmd:
            e = e.replace(':iter:', str(iter))
            res.append(e)
        return res
    
    if mode == MODE_NONE:
        mode = MODE_N
    
    if mode == MODE_N:
        pass
    elif mode == MODE_LIST:
        pass
    elif mode == MODE_GLOB:
        paths = []
        for g in globs:
            for p in glob.glob(g):
                if p not in paths:
                    paths.append(p)
        items = paths

    cmd0 = cmd[0]
    if ':iter:' in cmd0:
        pass
    else:
        if not is_executable(cmd0):
            raise ValueError("{} is not an executable".format(cmd0))

    for item in items:
        end = ' '
        proc, t = run(repl_iter(cmd, item), verbose=verbose, print_date=print_date, print_time=print_time, end=end)
        if newline:
            print(flush=True)
        if print_stat:
            print("{:.3f} s".format(t), file=sys.stderr)
        time.sleep(sleep)

if __name__ == "__main__":
    main()