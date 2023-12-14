from bashrange import expand_args

import time
import subprocess
from .shared import run

def print_help():
    print("""
usage: pyrepeat [-h] [--help] [-n COUNT] [-t SECONDS] [--timeout SECONDS] 
  [--at] [-v] [--sep-nl | --sep-sp] [--blank-line] command [args]

optional arguments:
  -n COUNT               run command COUNT times
  -t, --timeout SECONDS  sleep SECONDS between
  --at                   print current time and separator before executing command
  -v, --verbose          print command and separator before executing command
  --sep-nl               separator is newline
  --sep-sp               separator is space (default)
  --blank-line           print blank line after command output

examples:
  pyrepeat -n 5 echo hello world :iter:
  pyrepeat -n 10 -t 10 --blank-line pyexec tasklist "|" pygrep python
  pyrepeat -t 60 --at pynmap example.com -p 80
  pyrepeat -t 30 --blank-line pyfind build -mmin -0.1

runs command(s) n times or forever
""")

def main():
    args = expand_args()
    i = 0

    count = 0
    timeout = 0
    verbose = False
    sep_sp = True
    blank_line = False
    at = False

    while True:
        if args[i] in ['--help', '-h']:
            print_help()
            exit(0)
        elif args[i] in ['-n']:
            count = int(args[i+1])
            i += 2
        elif args[i] in ['-t', '--timeout']:
            timeout = float(args[i+1])
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

    iter = 0
    while True:
        iter += 1
        end = ' ' if sep_sp else '\n'
        run(repl_iter(cmd, iter), verbose=verbose, at=at, end=end)
        if blank_line:
            print(flush=True)
        if iter != count:
            time.sleep(timeout)
        if iter == count:
            break

if __name__ == "__main__":
    main()