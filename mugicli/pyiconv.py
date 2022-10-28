import argparse
from bashrange import expand_args
from . import read_stdin_bin, write_stdout_bin

def main():
    EXAMPLE_TEXT = """examples:
  tasklist | pyiconv -f cp866 | pygrep python
"""
    parser = argparse.ArgumentParser(prog="pyiconv", description="converts text from one encoding to another", epilog=EXAMPLE_TEXT, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-f', '--from', default='utf-8')
    parser.add_argument('-t', '--to', default='utf-8')
    args = parser.parse_args(expand_args())
    #print(args); exit(0)
    data = read_stdin_bin()
    text = data.decode(getattr(args, 'from'))
    data = text.encode(args.to)
    write_stdout_bin(data)

if __name__ == "__main__":
    main()