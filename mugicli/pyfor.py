from bashrange import expand_args

import time
from .shared import run, is_executable
import glob

def print_help():
    print("""
usage: pyfor [-h] [--help] [-n COUNT] [--list items...] [--glob exprs...] [--sleep SECONDS] 
  [--at] [-v] [--sep-nl | --sep-sp] [--blank-line] [--] command [args]

optional arguments:
  -n COUNT               run command COUNT times
  --list items...        run command for each item in list
  --glob items...        run command for each path matched by globs
  -s, --sleep SECONDS    sleep SECONDS after command
  --at                   print current time and separator before executing command
  -v, --verbose          print command and separator before executing command
  --sep-nl               separator is newline
  --sep-sp               separator is space (default)
  --blank-line           print blank line after command output

examples:
  pyfor -n 5 echo hello world :iter:
  pyfor -n 10 -s 10 --blank-line pyexec tasklist "|" pygrep python
  pyfor -s 60 --at pynmap example.com -p 80
  pyfor -s 30 --blank-line pyfind build -mmin -0.1
  pyfor --list pytrue pyfalse -- pyexec :iter: "&&" echo yeah :iter: "||" echo meh :iter:

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
    i = 0

    count = 0
    sleep = 0
    verbose = False
    sep_sp = True
    blank_line = False
    at = False
    items = []
    globs = []
    mode = MODE_NONE

    while True:
        if args[i] in ['--help', '-h']:
            print_help()
            exit(0)
        elif args[i] in ['-n']:
            count = int(args[i+1])
            i += 2
            if mode == MODE_NONE:
                mode = MODE_N
            else:
                raise ValueError("Use only one of: -n --list --glob")
        elif args[i] in ['-s', '--sleep']:
            sleep = float(args[i+1])
            i += 2
        elif args[i] in ['-v', '--verbose']:
            verbose = True
            i += 1
        elif args[i] in ['--blank-line']:
            blank_line = True
            i += 1
        elif args[i] == '--at':
            at = True
            i += 1
        elif args[i] == '--sep-sp':
            sep_sp = True
            i += 1
        elif args[i] == '--sep-nl':
            sep_sp = False
            i += 1
        elif args[i] == '--list':
            i += 1
            if mode == MODE_NONE:
                mode = MODE_LIST
            else:
                raise ValueError("Use only one of: -n --list --glob")
            while not args[i].startswith('-'):
                items.append(args[i])
                i += 1
        elif args[i] == '--glob':
            i += 1
            if mode == MODE_NONE:
                mode = MODE_GLOB
            else:
                raise ValueError("Use only one of: -n --list --glob")
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
        raise ValueError("Use one of: -n --list --glob")

    if mode == MODE_N:
        items = range(count)
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
        end = ' ' if sep_sp else '\n'
        run(repl_iter(cmd, item), verbose=verbose, at=at, end=end)
        if blank_line:
            print(flush=True)
        time.sleep(sleep)

if __name__ == "__main__":
    main()