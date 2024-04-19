import os
import argparse

from .shared import glob_paths
from . import format_size, read_stdin_lines
from bashrange import expand_args
from shortwalk import walk
from collections import defaultdict

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
    parser.add_argument("-o",'--order', choices=['s','c','size','count'], default='s', help='sort order')
    parser.add_argument('--skip-git', action='store_true')
    parser.add_argument('-X', '--xargs', action='store_true', help="read paths from stdin")
    parser.add_argument('--maxdepth', type=int, default=0)
    parser.add_argument('--sample', type=int, default=0)
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

    stat = defaultdict(lambda: (0, 0))
    sample = defaultdict(list)

    def append_stat(path):
        ext = os.path.splitext(path)[1]
        if len(ext) > 14:
            ext = ''
        count, size = stat[ext]
        count += 1
        size += os.path.getsize(path)
        stat[ext] = (count, size)
        if len(sample[ext]) < args.sample:
            sample[ext].append(os.path.basename(path))

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
            for root, dirs, files in walk(path, maxdepth=args.maxdepth):
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

    def sample_str(items):
        def q(s):
            if ' ' in s:
                return '"' + s + '"'
            return s
        return " ".join([q(e) for e in items])

    if args.human_readable:
        formatter = lambda c, s, p, smp: "{:7d} {} {:14s} {}".format(c, format_size(s, 7), p, sample_str(smp))
    else:
        formatter = lambda c, s, p, smp: "{:7d} {:12d} {:14s} {}".format(c, s, p, sample_str(smp))

    p = Printer(args.cli)
    reported_size = 0
    reported_count = 0

    if args.human_readable:
        header_format = "{:7s} {:7s} {:14s} {}"
    else:
        header_format = "{:7s} {:12s} {:14s} {}"
    header_cols = ["Count", "Size", "Ext"]
    if args.sample > 0:
        header_cols.append("Sample")
    else:
        header_cols.append("")
    print(header_format.format(*header_cols))
    for ext, count, size in stat_list:
        p.print(formatter(count, size, ext, sample[ext]))
        p.set_item(count, size, ext)
        reported_size += size
        reported_count += count
        if args.short and shortener(reported_count, reported_size, total_count, total_size):
            p.print("...")
            p.print(formatter(total_count - reported_count, total_size - reported_size, "other", []))
            p.set_other(total_count - reported_count, total_size - reported_size)
            break
    p.print("---")
    p.print(formatter(total_count, total_size, "total", []))
    p.set_total(total_count, total_size)

    if not args.cli:
        return p.result()

if __name__ == "__main__":
    main()