import argparse
from . import read_stdin_lines
from bashrange import expand_args

def uniq_ordered(items):
    res = []
    for item in items:
        if item not in res:
            res.append(item)
    return res

def main():

    example_text = """examples:
  echo %PATH%| pytr ; \\n | pygrep -i conda | pysetpath -o env.bat
"""

    parser = argparse.ArgumentParser(prog='pysetpath', description='reads dirs from stdin and prints set path expression', epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-o','--output', help='output path')
    parser.add_argument('-a', '--append', action='store_true')
    parser.add_argument('-p', '--prepend', action='store_true')
    parser.add_argument('-r', '--reset', action='store_true')
    args = parser.parse_args(expand_args())
    lines = uniq_ordered([l for l in read_stdin_lines(drop_last = True, rstrip = True) if l != ''])

    if args.reset:
        exp = 'set PATH={}'.format(";".join(lines))
    elif args.append:
        exp = 'set PATH=%PATH%;{}'.format(";".join(lines))
    else: # prepend by default
        exp = 'set PATH={};%PATH%'.format(";".join(lines))

    if args.output:
        with open(args.output, "w") as f:
            f.write(exp)
    else:
        print(exp)

if __name__ == "__main__":
    main()
