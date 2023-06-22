from bashrange import expand_args
from .shared import run_many
import time

def print_help():
    print("""
usage: pyrepeat [-h] [--help] [-n COUNT] [-t SECONDS] [--timeout SECONDS] [-v] [--verbose] program

optional arguments:
  -n COUNT               run command COUNT times
  -t, --timeout SECONDS  sleep SECONDS between
  -v, --verbose          print command
  --newline              print blank line after result

examples:
  pyrepeat -n 100 -t 3 --newline tasklist "|" pyiconv -f cp866 "|" pygrep python
  pyrepeat -n 100 -t 3 --newline tasklist "|" pyiconv -f cp866 "|" pygrep "g[+][+]|cc1plus|mingw32"
  pyrepeat -t 30 --newline pyfind build -mmin -0.1

runs command(s) n times or forever
""")

def main():
    args = expand_args()
    i = 0

    count = 0
    timeout = 0
    verbose = False
    newline = False

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
        elif args[i] in ['--newline']:
            newline = True
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
            if e == 'ITER':
                e = str(iter)
            else:
                e = e.replace('${ITER}', str(iter))
            res.append(e)
        return res

    iter = 0
    while True:
        iter += 1
        run_many(repl_iter(cmd, iter), verbose=verbose)
        if newline:
            print(flush=True)
        if iter != count:
            time.sleep(timeout)
        if iter == count:
            break

if __name__ == "__main__":
    main()