import argparse
import os

from collections import defaultdict
from itertools import count, zip_longest
import re
from .shared import glob_paths

# todo cleanup unused code
# todo human readible
# todo summary
# todo --files

def int_ceil(num, den):
    return (num + den - 1) // den

def is_path_in(path1, path2):
    if len(path1) < len(path2):
        return False
    for n1, n2 in zip(path1, path2):
        if n1 != n2:
            return False
    return True

def count_equal(it1, it2):
    for i, v1, v2 in zip(count(), it1, it2):
        if v1 != v2:
            return i-1
    return i-1

def path_split_(path):
    path_ = re.split('[/\\\\]', path)
    if re.match('^[a-z]:$',path_[0], re.IGNORECASE):
        path_[0] = path_[0] + '\\'
    return path_

def path_split(path):
    res = []
    rx = re.compile('^([a-z]:\\\\|\\/)$', re.IGNORECASE)
    while True:
        head, tail = os.path.split(path)
        res.append(tail)
        path = head
        if head == '':
            return list(reversed(res))
        if rx.match(head):
            res.append(head)
            return list(reversed(res))

def without_none(items):
    return [v for v in items if v is not None]

def path_diff(path1, path2):
    
    comm = []
    res1 = []
    res2 = []

    is_comm = True
    for n1, n2 in zip_longest(path_split(path1), path_split(path2), fillvalue=None):
        if is_comm:
            if None in [n1, n2]:
                is_comm = False
            else:
                is_comm = n1 == n2
        if is_comm:
            comm.append(n1)
        else:
            res1.append(n1)
            res2.append(n2)
    
    return comm, without_none(res1), without_none(res2)

class Printer:
    def print(self, size, path):
        print("{:10d} {}".format(int_ceil(size, 1024), path))
        pass

class DirStat:
    def __init__(self, printer):
        self._flushed = set()
        self._stat = defaultdict(int)
        self._printer = printer
        self._prev = None

        self._queue = []

    def add_file(self, root, f):
        path = os.path.join(root, f)
        size = os.path.getsize(path)
        path_ = path_split(path)
        for n in range(1, len(path_)):
            self._stat[os.path.join(*path_[:n])] += size
        #self._printer.print(size, path)

    def add_dir(self, root, d):
        path = os.path.join(root, d)
        self._stat[path] = 0

    def begin(self, path):
        self._root = path

    def end(self):
        self.add_root(os.path.dirname(self._root))
        self._queue = []

    def add_root(self, root):

        def pop_queue():
            for i, path in enumerate(self._queue):
                if not root.startswith(path):
                    return self._queue.pop(i)
        
        while True:
            path = pop_queue()
            if path is None:
                break
            #print("flush {}".format(path))
            self._printer.print(self._stat[path], path)
        
        self._queue = [root] + self._queue

    def add_root_(self, root):
        if self._prev is None:
            self._prev = root
            return

        #print(root)

        #print(*path_diff(self._prev, root))
        comm, prev, root_ = path_diff(self._prev, root)

        if len(prev) > 1:
            """
            for i in range(1,len(prev)+1):
                path_ = comm + prev[:i]
                #print(path_)
                print("flush " + os.path.join(*path_))
            """
            path_ = os.path.join(*(comm + [prev[0]]))
            for path, size in self._stat.items():
                if path in self._flushed:
                    continue
                if path.startswith(path_):
                    #print("flush " + path)
                    self._printer.print(size, path)
                self._flushed.add(path)

        self._prev = root

        #print('add_root', root)
        """
        root_ = os.path.split(root)
        for root2, size in self._stat.items():
            if root2 == self._root:
                continue
            if root2 in self._flushed:
                continue
            root2_ = os.path.split(root2)
            if not is_path_in(root2_, root_):
                #print('{} not in {}'.format(root2, root))
                self._flushed.add(root2)
                self._printer.print(size, root2)
        """

def main():
    parser = argparse.ArgumentParser(add_help=False, description='prints directories sizes')
    parser.add_argument('-s',action='store_true', help='print only summary')
    parser.add_argument('-h',action='store_true', help='print in human readible units')
    parser.add_argument('path', nargs='*', help='path to calculate')
    parser.add_argument('--help', action='help')

    args = parser.parse_args()

    paths = glob_paths(args.path)
    if len(paths) == 0:
        paths.append(os.getcwd())

    #print(paths); exit(0)

    printer = Printer()

    stat = DirStat(printer)

    for path in paths:
        #print('os.walk(path)', path)
        stat.begin(path)
        for root, dirs, files in os.walk(path):
            stat.add_root(root)
            for d in dirs:
                stat.add_dir(root, d)
            for f in files:
                stat.add_file(root, f)
        stat.end()

if __name__ == "__main__":
    main()