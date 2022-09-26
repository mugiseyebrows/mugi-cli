import argparse
from time import sleep
from . import parse_time_arg
from bashrange import expand_args

def main():
    example_text = """examples:
  pysleep 1m && taskkill 
"""
    parser = argparse.ArgumentParser(prog='pysleep', description='sleeps for TIME seconds', epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("time")
    args = parser.parse_args(expand_args())
    time = parse_time_arg(args.time)
    sleep(time)

if __name__ == "__main__":
    main()