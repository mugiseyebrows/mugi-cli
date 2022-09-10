from . import print_utf8
import os
import sys
import textwrap

def print_help():
    print(textwrap.dedent("""\
    usage: pycwd [-h] [--help]

    prints current working directory
    """))

def main():
    args = sys.argv[1:]
    if '-h' in args or '--help' in args:
        print_help()
        return
    print_utf8(os.getcwd())
if __name__ == "__main__":
    main()