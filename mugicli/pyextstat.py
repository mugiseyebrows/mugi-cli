import os
import argparse

from .shared import glob_paths
from . import format_size, read_stdin_lines
from bashrange import expand_args

class Args:
    def __init__(self, path, short=False, human_readable=False, order='s', skip_git=False, xargs=False):

        if isinstance(path, str):
            self.path = [path]
        else:
            self.path = path
            
        self.short = short
        self.human_readable = human_readable
        self.order = order
        self.skip_git = skip_git
        self.xargs = xargs
        self.cli = False

def main():
    parser = argparse.ArgumentParser(description='prints file extension statistics', add_help=False)
    parser.add_argument("path", nargs="*", help="paths")
    parser.add_argument('-s', '--short', action='store_true', help='show short list')
    parser.add_argument('--help', action='help', help="show help")
    parser.add_argument('-h', '--human-readable', action='store_true', help='human readable sizes')
    parser.add_argument('--order', choices=['s','c','size','count'], default='s', help='sort order')
    parser.add_argument('--skip-git', action='store_true')
    parser.add_argument('-X', '--xargs', action='store_true', help="read paths from stdin")
    #parser.add_argument('-o', '--output', help="output to file")
    args = parser.parse_args(expand_args())
    args.cli = True
    extstat(args)

class Printer:
    def __init__(self, cli):
        self._cli = cli
        self._items = []
        self._other = None
        self._total = None

    def print(self, msg):
        if self._cli:
            print(msg)

    def set_item(self, count, size, ext):
        self._items.append((count, size, ext))

    def set_other(self, count, size):
        self._other = (count, size)

    def set_total(self, count, size):
        self._total = (count, size)

    def result(self):
        return self._items, self._other, self._total

def extstat(args):

    stat = dict()

    def append_stat(path):
        ext = os.path.splitext(path)[1]
        if ext not in stat:
            stat[ext] = (0, 0)
        count = stat[ext][0]
        size = stat[ext][1]
        count += 1
        size += os.path.getsize(path)
        stat[ext] = (count, size)            

    if args.xargs:
        paths = read_stdin_lines(drop_last=True, rstrip=True)
    else:
        if len(args.path) == 0:
            paths = ['.']
        else:
            paths = glob_paths(args.path)

    for path in paths:
        if os.path.isfile(path):
            append_stat(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    try:
                        append_stat(os.path.join(root, f))
                    except FileNotFoundError:
                        pass
                if args.skip_git and '.git' in dirs:
                    dirs.remove('.git')
        else:
            print("{} not a dir nor a file".format(path))

    total_count = sum([v[0] for v in stat.values()])
    total_size = sum([v[1] for v in stat.values()])
    stat_list = [(ext, count, size) for ext, (count, size) in stat.items()]

    if args.order in [None, 's', 'size']:
        sort_key = lambda item: item[2]
        shortener = lambda rc, rs, tc, ts: rs / ts > 0.9
    else:
        sort_key = lambda item: item[1]
        shortener = lambda rc, rs, tc, ts: rc / tc > 0.9

    stat_list.sort(key = sort_key, reverse=True)

    if args.human_readable:
        formatter = lambda c, s, p: "{:7d} {} {}".format(c, format_size(s, 7), p)
    else:
        formatter = lambda c, s, p: "{:7d} {:7d} {}".format(c, s, p)

    p = Printer(args.cli)
    reported_size = 0
    reported_count = 0
    for ext, count, size in stat_list:
        p.print(formatter(count, size, ext))
        p.set_item(count, size, ext)
        reported_size += size
        reported_count += count
        if args.short and shortener(reported_count, reported_size, total_count, total_size):
            p.print("...")
            p.print(formatter(total_count - reported_count, total_size - reported_size, "other"))
            p.set_other(total_count - reported_count, total_size - reported_size)
            break
    p.print("---")
    p.print(formatter(total_count, total_size, "total"))
    p.set_total(total_count, total_size)

    if not args.cli:
        return p.result()

if __name__ == "__main__":
    main()