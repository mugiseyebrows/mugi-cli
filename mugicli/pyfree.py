import argparse
from . import format_size_g
try:
    import psutil
except ImportError:
    pass

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--help", action='help')
    parser.add_argument("-h","-g","-G",action='store_true')

    args = parser.parse_args()
    #print(args); exit(0)

    m = psutil.virtual_memory()
    total = m.total
    free = m.available
    used = total - free

    print("{:>15} {:>15} {:>15}".format("total","used","free"))
    if args.h:
        print("{} {} {}".format(*[format_size_g(v, 15) for v in [total, used, free]]))
    else:
        print("{:15} {:15} {:15}".format(total, used, free))

if __name__ == "__main__":
    main()