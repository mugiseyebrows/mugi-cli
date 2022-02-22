import subprocess
import time
import sys
from .shared import eprint, run
import textwrap

def print_help():
    print(textwrap.dedent("""\
    usage: pytime program [...args]

    measures execution time of application
    """))

def main():
    t1 = time.time()
    
    args = sys.argv[1:]

    if args[0] in ['-h', '--help']:
        print_help()
        return

    #print(args)
    run(args)
    
    t2 = time.time()
    eprint("{:.3f}s".format(t2 - t1))

if __name__ == "__main__":
    main()