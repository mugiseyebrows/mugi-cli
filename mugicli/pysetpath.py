import argparse
import shutil
from . import read_stdin_lines
from bashrange import expand_args
from .shared import stdout_codec
import os
import re
import sys

def uniq_ordered(items):
    res = []
    for item in items:
        if item not in res:
            res.append(item)
    return res

def main():

    example_text = """examples:
  pysetpath -g conda -o conda-env.bat
  pysetpath -w gcc cmake ninja -o mingw-env.bat
  type bindirs.txt | pysetpath --xargs -o env.bat
"""

    parser = argparse.ArgumentParser(prog='pysetpath', description='reads PATH env variable (or dirs from stdin) and prints set path expression', epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-o','--output', help='output path')
    parser.add_argument('-a', '--append', action='store_true')
    parser.add_argument('-p', '--prepend', action='store_true')
    parser.add_argument('-r', '--reset', action='store_true')
    parser.add_argument('-X', '--xargs', action='store_true', help='read paths from stdin')
    parser.add_argument('-g', '--grep', nargs='+', help='filter paths by patterns')
    parser.add_argument('-w', '--which', nargs="+", help='add executable path')
    parser.add_argument('-u', '--user-profile', action='store_true', help='replace %USERPROFILE% value with variable name')
    args = parser.parse_args(expand_args())

    #print(args); exit(0)

    if args.xargs:
        paths = uniq_ordered([l for l in read_stdin_lines(drop_last = True, rstrip = True) if l != ''])
    else:
        paths = []
        if args.which is not None:
            for cmd in args.which:
                paths.append(os.path.dirname(shutil.which(cmd)))
        if args.grep is not None:
            env_paths = os.environ['PATH'].split(';')
            for pattern in args.grep:
                for path in env_paths:
                    if re.search(pattern, path):
                        paths.append(path)
        paths = uniq_ordered(paths)

    if args.user_profile:
        user_profile = os.environ['USERPROFILE']
        paths = [path.replace(user_profile, "%USERPROFILE%") for path in paths]

    if args.reset:
        exp = 'set PATH={}'.format(";".join(paths))
    elif args.append:
        exp = 'set PATH=%PATH%;{}'.format(";".join(paths))
    else: # prepend by default
        exp = 'set PATH={};%PATH%'.format(";".join(paths))

    if args.output:
        with open(args.output, "w", encoding=stdout_codec) as f:
            f.write(exp)
    else:
        sys.stdout.buffer.write(exp.encode(stdout_codec))

if __name__ == "__main__":
    main()
