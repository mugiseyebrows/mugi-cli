import re
import os
import sys
from .shared import parse_args

"""
def parse_args(args):
    opts = {
        '-e': False,
        '-n': False,
        '-ne': False,
        '-en': False
    }
    while args[0] in opts.keys():
        opt = args.pop(0)
        opts[opt] = True
    if opts['-ne'] or opts['-en']:
        opts['-n'] = True
        opts['-e'] = True
    return opts, args
"""

def print_help():
    print("""usage: pyecho [-e] [-n] [args...]

prints text to stdout

optional arguments:
-h --help  show this message and exit
-e         decode escape sequences
-n         do not print newline
""")
    
def main():
    """
    def env_vars(m):
        n = m.group(1)
        if n in os.environ:
            return os.environ[n]
        return '%' + n + '%'
    def expand_vars(arg):
        return re.sub("%([^%]*)%", env_vars, arg)
    """

    def unescape(arg):
        return arg.encode('utf-8').decode('unicode_escape')

    #print(sys.argv)

    opts, args = parse_args(['e','n','h'],['help'],[],[],sys.argv[1:])

    if opts['h'] or opts['help']:
        print_help()
        return

    if opts['e']:
        transform = unescape
    else:
        transform = lambda arg: arg
        
    args = [transform(arg) for arg in args]
    text = " ".join(args)
    sys.stdout.buffer.write(text.encode('utf-8'))
    if not opts['n']:
        sys.stdout.buffer.write(b'\n')

if __name__ == "__main__":
    main()