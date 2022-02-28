import sys
import re
from .shared import eprint

def print_help():
    print("""Print numbers from FIRST to LAST with INCREMENT
seq LAST
seq FIRST LAST
seq FIRST INCREMENT LAST
""")

def map_number(args):
    if all([re.match('^[0-9]+$', item) is not None for item in args]):
        return map(int, args), -1
    prec = max([len(item.split('.')[1]) if '.' in item else -1 for item in args])
    return map(float, args), prec

def print_number(n, prec):
    if prec > -1:
        print(("{:." + str(int(prec)) + "f}").format(n))
    else:
        print(n)

def main():
    args = sys.argv[1:]

    if '-h' in args or '--help' in args:
        print_help()
        return

    first = 1
    inc = 1
    last = 0
    prec = -1
    if len(args) == 3:
        (first, inc, last), prec = map_number(args)
    elif len(args) == 2:
        (first, last), prec = map_number(args)
    elif len(args) == 1:
        (last, ), prec = map_number(args)
    else:
        print_help()
        return
    
    i = first

    if inc == 0:
        eprint('inc must be non-zero')
        exit(1)

    elif inc > 0:
        while i <= last:
            print_number(i, prec)
            i += inc
    else:
        while i >= last:
            print_number(i, prec)
            i += inc

if __name__ == "__main__":
    main()