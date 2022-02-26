import os
import argparse
from .shared import glob_paths_dirs
from . import read_stdin_text

def main():
    parser = argparse.ArgumentParser(description='prints file extension statistics')
    parser.add_argument("path", nargs="*", help="paths")
    parser.add_argument('-s', '--short', action='store_true')

    args = parser.parse_args()
    
    stat = dict()
    if len(args.path) == 0:
        # read paths from stdin
        text = read_stdin_text()
        for line in text.split('\n'):
            line = line.rstrip()
            ext = os.path.splitext(line)[1]
            if ext not in stat:
                stat[ext] = 0
            stat[ext] += 1
    else:
        # walk paths
        paths = glob_paths_dirs(args.path)
        for path in paths:
            for root, dirs, files in os.walk(path):
                for f in files:
                    ext = os.path.splitext(f)[1]
                    if ext not in stat:
                        stat[ext] = 0
                    stat[ext] += 1

    total = sum(stat.values())
    stat_ = [(ext, count) for ext, count in stat.items()]
    stat_.sort(key= lambda item: item[1], reverse=True)

    t = 0
    for ext, count in stat_:
        print("{:7d} {}".format(count, ext))
        t += count
        if args.short and t / total > 0.9:
            print("{:7d} {}".format(total-t, "other"))
            break
    print("{:7d} {}".format(total, "total"))

if __name__ == "__main__":
    main()