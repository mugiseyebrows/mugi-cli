import sys
from .shared import print_lines, glob_paths, read_lines
import re
import argparse

# todo backreferences
# todo -i

def main():
    pass

def parse_exprs(exprs):
    res = []
    for arg in exprs:
        if not arg.startswith("s"):
            raise ValueError("Unexpected expression {}".format(arg))
        sep = arg[1]
        exp = arg.split(sep)
        flags = ""
        if len(exp) == 3: # allow unterminated regexp
            s, subj, repl = exp
        elif len(exp) == 4:
            s, subj, repl, flags = exp
        else:
            raise ValueError("invalid expr {}".format(exp))
        res.append((subj, repl, flags))
    return res

def main():
    
    one_expr = '-e' not in sys.argv[1:]

    parser = argparse.ArgumentParser(description='replaces text')
    if one_expr:
        parser.add_argument('expr')
    parser.add_argument('-e', action='append', help='expression')
    parser.add_argument('path', nargs='*')
    
    args = parser.parse_args()

    if one_expr:
        exprs = parse_exprs([args.expr])
    else:
        exprs = parse_exprs(args.e)

    #print(args); exit(0)

    paths = glob_paths(args.path)
    lines = read_lines(paths)

    def replace(line):
        for subj, repl, flags in exprs:
            flags_ = re.IGNORECASE if 'i' in flags else 0
            line = re.sub(subj, repl, line, flags=flags_)
        return line

    lines = map(replace, lines)
    print_lines(lines)

if __name__ == "__main__":
    main()        
