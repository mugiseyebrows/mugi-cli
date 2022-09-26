import argparse
from . import print_utf8
import os
from bashrange import expand_args

def main():
    parser = argparse.ArgumentParser(prog="pycwd", description="prints current working directory")
    parser.parse_args(expand_args())
    print_utf8(os.getcwd())

if __name__ == "__main__":
    main()