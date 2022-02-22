import os
import argparse
from .shared import glob_paths_dirs

def main():
    parser = argparse.ArgumentParser(description='prints extension statistics')
    parser.add_argument("paths", nargs="*", type=str, help="paths")
    parser.add_argument('-s', '--short', action='store_true', help='short statistics')
    args = parser.parse_args()
    paths = glob_paths_dirs(args.paths)
    if len(args.paths) == 0:
        paths = ["."]
    stat = dict()
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