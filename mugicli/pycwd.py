import argparse
from . import print_utf8
import os
import sys
import textwrap

def main():
    parser = argparse.ArgumentParser(prog="pycwd", description="prints current working directory")
    parser.parse_args()
    print_utf8(os.getcwd())

if __name__ == "__main__":
    main()