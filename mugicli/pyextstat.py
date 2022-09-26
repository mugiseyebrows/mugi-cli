import os
import argparse

from .shared import glob_paths_dirs
from . import format_size, read_stdin_lines
from bashrange import expand_args

def main():
    parser = argparse.ArgumentParser(description='prints file extension statistics', add_help=False)
    parser.add_argument("path", nargs="*", help="paths")
    parser.add_argument('-s', '--short', action='store_true', help='show short list')
    parser.add_argument('--help', action='help', help="show help")
    parser.add_argument('-h', action='store_true', help='human readable sizes')
    parser.add_argument('--order', '-o', choices=['s','c','size','count'], help='sort order')
    parser.add_argument('--skip-git', action='store_true')

    args = parser.parse_args(expand_args())

    #print(args); exit(0)
    
    stat = dict()

    def append_stat(path):
        ext = os.path.splitext(path)[1]
        if ext not in stat:
            stat[ext] = (0, 0)
        count = stat[ext][0]
        size = stat[ext][1]
        count += 1
        size += os.path.getsize(os.path.join(root, f))
        stat[ext] = (count, size)            
    
    if len(args.path) == 0:
        # read paths from stdin
        lines = read_stdin_lines(drop_last=True, rstrip=True)
        for line in lines:
            append_stat(line)
    else:
        # walk paths
        paths = glob_paths_dirs(args.path)
        for path in paths:
            for root, dirs, files in os.walk(path):
                for f in files:
                    append_stat(os.path.join(root, f))
                if args.skip_git and '.git' in dirs:
                    dirs.remove('.git')

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

    if args.h:
        formatter = lambda c, s, p: "{:7d} {} {}".format(c, format_size(s, 7), p)
    else:
        formatter = lambda c, s, p: "{:7d} {:7d} {}".format(c, s, p)

    reported_size = 0
    reported_count = 0
    for ext, count, size in stat_list:
        print(formatter(count, size, ext))
        reported_size += size
        reported_count += count
        if args.short and shortener(reported_count, reported_size, total_count, total_size):
            print("...")
            print(formatter(total_count - reported_count, total_size - reported_size, "other"))
            break
    print("---")
    print(formatter(total_count, total_size, "total"))

if __name__ == "__main__":
    main()