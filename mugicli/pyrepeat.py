from bashrange import expand_args
from .shared import run_many
import time

def print_help():
    print("""
usage: pyrepeat [-h] [--help] [--forever] [-c COUNT] [--count COUNT] [-t SECONDS] [--timeout SECONDS] [-v] [--verbose] program

optional arguments:
  -c, --count COUNT      run command COUNT times
  -t, --timeout SECONDS  sleep SECONDS between 
  -v, --verbose          print command

examples:
  pyrepeat -c 100 -t 1 tasklist "|" pyiconv -f cp866 "|" pygrep python

runs command(s) n times
""")

def main():
    args = expand_args()
    i = 0

    count = 0
    timeout = 0
    verbose = False

    while True:
        if args[i] in ['--help', '-h']:
            print_help()
            exit(0)
        elif args[i] == '--forever':
            count = 0
            i += 1
        elif args[i] in ['-c', '--count']:
            count = int(args[i+1])
            i += 2
        elif args[i] in ['-t', '--timeout']:
            timeout = float(args[i+1])
            i += 2
        elif args[i] in ['-v', '--verbose']:
            verbose = True
            i += 1
        else:
            cmd = args[i:]
            break
    
    iter = 0
    while True:
        iter += 1
        run_many(cmd, verbose=verbose)
        if iter != count:
            time.sleep(timeout)
        if iter == count:
            break

if __name__ == "__main__":
    main()