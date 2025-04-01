import argparse
import os
from . import print_utf8

def main():
    parser = argparse.ArgumentParser(prog='pypwd', description='prints current directory')
    args = parser.parse_args()
    print_utf8(os.path.realpath(os.getcwd()))

if __name__ == "__main__":
    main()