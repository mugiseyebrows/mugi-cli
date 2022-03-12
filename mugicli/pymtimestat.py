import re
import os
import argparse

from .shared import glob_paths, glob_paths_dirs
import datetime
import json
import fnmatch
from . import parse_time_arg

def median(vs):
    if len(vs) % 2:
        return vs[len(vs) // 2]
    else:
        return (vs[len(vs) // 2 - 1] + vs[len(vs) // 2]) / 2

def average(vs):
    return sum(vs) / len(vs)


def include_exclude(include, exclude, name):
    if include is None and exclude is None:
        return True
    if include is None:
        ok = True
    else:
        ok = False
        for pat in include:
            if fnmatch.fnmatch(name, pat):
                ok = True
    if not ok:
        return False
    if exclude is None:
        return True
    else:
        for pat in exclude:
            if fnmatch.fnmatch(name, pat):
                return False
    return True

def main():
    parser = argparse.ArgumentParser(description='prints mtime statistics')
    parser.add_argument('path', nargs='*')

    parser.add_argument('-r', '--recent', help='print recently changed files (max(mtime) - mtime <= N)')
    parser.add_argument('-o', '--old', help='print long ago changed files (mtime - min(mtime) <= N)')
    parser.add_argument('-a', '--average', help='print files changed within N seconds around average (abs(average(mtime) - mtime) <= N)')
    parser.add_argument('-i', '--include', nargs='+', help='include files glob')
    parser.add_argument('-e', '--exclude', nargs='+', help='include files glob')

    args = parser.parse_args()

    #print(args)

    stat = []

    if len(args.path) == 0:
        paths = ["."]
    else:
        paths = glob_paths_dirs(args.path)
    mtime = []
    for path in paths:
        for root, dirs, files in os.walk(path):
            for f in files + dirs:
                if not include_exclude(args.include, args.exclude, f):
                    continue
                p = os.path.join(root, f)
                t = os.path.getmtime(p)
                stat.append({"t":t, "p": p})
                mtime.append(t)

    if len(mtime) == 0:
        print("No files")
        exit(1)

    mtime.sort()

    names = ['min', 'max', 'average', 'median']

    min_mtime = min(mtime)
    max_mtime = max(mtime)
    avg_mtime = average(mtime)

    values = [min_mtime, max_mtime, avg_mtime, median(mtime)]

    if args.recent or args.old or args.average:
        
        if args.recent:
            arg_recent = parse_time_arg(args.recent)
        else:
            arg_recent = None

        if args.old:
            arg_old = parse_time_arg(args.old)
        else:
            arg_old = None
        
        if args.average:
            arg_average = parse_time_arg(args.average)
        else:
            arg_average = None

        #print("arg_recent {}, arg_old {}, arg_average {}".format(arg_recent, arg_old, arg_average))

        for path in paths:
            for root, dirs, files in os.walk(path):
                for f in files + dirs:

                    if not include_exclude(args.include, args.exclude, f):
                        continue

                    p = os.path.join(root, f)
                    t = os.path.getmtime(p)

                    do_print = False
                    if arg_recent is not None:
                        if max_mtime - t <= arg_recent:
                            do_print = True
                    if arg_old is not None:
                        if t - min_mtime <= arg_old:
                            do_print = True
                    if arg_average is not None:
                        if abs(t - avg_mtime) <= arg_average:
                            do_print = True
                    
                    if do_print:
                        if os.path.isabs(path):
                            p_ = p
                        else:
                            p_ = os.path.relpath(p, os.getcwd())
                        print("{} {}".format(datetime.datetime.fromtimestamp(t), p_))

    print("{:8} files".format(len(mtime)))
    for n,v in zip(names, values):
        print("{:8} {}".format(n, datetime.datetime.fromtimestamp(v)))

if __name__ == "__main__":
    main()