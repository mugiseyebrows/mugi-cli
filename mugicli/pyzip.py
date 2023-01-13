from ast import parse
import os
import argparse
import zipfile
from zipfile import ZIP_STORED, ZIP_DEFLATED, ZIP_BZIP2, ZIP_LZMA
from .shared import glob_paths, has_magic
from . import read_file_text, print_utf8, read_stdin_lines, read_file_lines
from bashrange import expand_args
from collections import defaultdict
import re
import fnmatch
import posixpath
import shutil
import chardet

# todo read from stdin
# todo ouput to stdout
# todo concat zips and files
# todo strip path, prepend path
# todo include exclude
# todo calculate hash of files
# todo gz xz bz2

def encode_decode(path):
    try:
        encoded = path.encode('cp437')
        det = chardet.detect(encoded)
        return encoded.decode(det['encoding'])
    except UnicodeEncodeError as e:
        return path
    except UnicodeDecodeError as e:
        return path

def path_to_list(path):
    res = re.split('[\\\\/]', path)
    if re.match('^[a-z]:$', res[0], re.IGNORECASE):
        res[0] = res[0] + '/'
    return res

def normalize_path(path):
    return posixpath.join(*path_to_list(path))

def split_list(items, pred):
    pos = []
    neg = []
    for item in items:
        if pred(item):
            pos.append(item)
        else:
            neg.append(item)
    return pos, neg

class Matcher:
    def __init__(self, include = None, exclude = None):
        if include:
            include_globs, include_nonglobs = split_list(include, lambda item: '*' in item)
        else:
            include_globs, include_nonglobs = [], []
        if exclude:
            exclude_globs, exclude_nonglobs = split_list(exclude, lambda item: '*' in item)
        else:
            exclude_globs, exclude_nonglobs = [], []
        self._include = include_globs, include_nonglobs
        self._exclude = exclude_globs, exclude_nonglobs

    def match(self, filename):
        include_globs, include_nonglobs = self._include
        exclude_globs, exclude_nonglobs = self._exclude
        basename = os.path.basename(filename)
        for pat in exclude_globs:
            if fnmatch.fnmatch(basename, pat):
                return False
            if fnmatch.fnmatch(filename, pat):
                return False
        for pat in exclude_nonglobs:
            if pat == basename:
                return False
            if pat == filename:
                return False


class Helper:
    def __init__(self, zipFile: zipfile.ZipFile):
        self._zipFile = zipFile
        filenames = []
        ZIP_FILENAME_UTF8_FLAG = 0x800
        for info in zipFile.filelist:
            if info.flag_bits & ZIP_FILENAME_UTF8_FLAG:
                filename = info.filename
            else:
                filename = encode_decode(info.filename)
            filenames.append((info.filename, filename))
        self._filenames = filenames

    def is_dir(self, path):
        path = normalize_path(path) + "/"
        for _, filename in self._filenames:
            if filename == path:
                return True
            if filename.startswith(path):
                return True
        return False
    
    def match(self, pattern):
        res = []
        for item in self._filenames:
            _, filename = item
            if filename.endswith('/'):
                continue
            if fnmatch.fnmatch(os.path.basename(filename), pattern):
                res.append(item)
        return res

    def file(self, path):
        path = normalize_path(path)
        for item in self._filenames:
            _, filename = item
            if path == filename:
                return item

    def dirs(self):
        res = []
        for item in self._filenames:
            _, filename = item
            if filename.endswith('/'):
                res.append(item)
        return res

    def files(self):
        res = []
        for item in self._filenames:
            _, filename = item
            if not filename.endswith('/'):
                res.append(item)
        return res

    def filenames(self):
        return self._filenames

    def listdir(self, path):
        path = normalize_path(path)
        res = []
        for item in self._filenames:
            _, filename = item
            if filename.startswith(path):
                res.append(item)
        return res

def main():

    COMPRESSION_METHODS = {
        'deflate': ZIP_DEFLATED,
        'd': ZIP_DEFLATED,
        'lzma': ZIP_LZMA,
        'l': ZIP_LZMA,
        'bzip2': ZIP_BZIP2,
        'b': ZIP_BZIP2,
        'store': ZIP_STORED,
        's': ZIP_STORED
    }

    parser = argparse.ArgumentParser(description='appends, extracts and list contents of zip archive')
    parser.add_argument('command', choices=['a','x','l'], help='add extract list') # todo u - update
    # list
    parser.add_argument('--type', choices=['d','f'], help='list only files or only dirs')
    parser.add_argument('--depth', type=int, help='list depth', default=0)
    # add
    parser.add_argument('--strip', type=int, help='strip n path components')
    parser.add_argument('--prepend', help='prepend to path')
    parser.add_argument('--include', '-i', nargs='+', help='paths or globs to exclude')
    parser.add_argument('--exclude', '-e', nargs='+', help='paths or globs to include')
    parser.add_argument('--list', help='path to list of files')
    parser.add_argument('--stdin', action='store_true', help='read paths from stdin')

    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('-m', choices=list(COMPRESSION_METHODS.keys()), help='compression method')
    parser.add_argument('-l', type=int, help="compression level 0..9 for deflate (0 - best speed, 9 - best compression) 1..9 for bzip2, has no effect if method is store or lzma")
    parser.add_argument('--base', help='base directory')
    
    

    parser.add_argument('-s', '--silent', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('zip')
    parser.add_argument('sources', nargs='*')
    args = parser.parse_args(expand_args())

    #print(args); exit(0)

    dst_base = args.output if args.output is not None else os.getcwd()

    compresslevel = args.l

    if args.verbose and args.silent:
        print_utf8('choose one: verbose or silent')
        exit(1)

    verbose = args.verbose or not args.silent

    if args.command == 'a':

        if args.stdin:
            paths = read_stdin_lines()
        elif args.list:
            paths = read_file_lines(args.list)
        else:
            paths = glob_paths(args.sources)

        compression = COMPRESSION_METHODS[args.m] if args.m is not None else ZIP_DEFLATED

        def add_file(zf, p, base):
            relpath = os.path.relpath(p, base)
            if args.strip:
                relpath = os.path.join(*re.split('[\\\\/]', relpath)[args.strip:])
            if args.prepend:
                relpath = os.path.join(args.prepend, relpath)
            if verbose:
                print_utf8(p)
            zf.write(p, relpath)

        with zipfile.ZipFile(args.zip, 'a', compression=compression, compresslevel=compresslevel) as zf:
            for path in paths:
                if args.base is None:
                    if os.path.isabs(path):
                        base = os.path.dirname(path)
                    else:
                        base = os.getcwd()
                else:
                    base = args.base

                include_globs = []
                include_nonglobs = []
                exclude_globs = []
                exclude_nonglobs = []

                
                if args.include:
                    include_globs, include_nonglobs = split_list(args.include, has_magic)
                if args.exclude:
                    exclude_globs, exclude_nonglobs = split_list(args.exclude, has_magic)

                def include_not_exclude(name):
                    if args.exclude:
                        if name in exclude_nonglobs:
                            return False
                        for pat in exclude_globs:
                            if fnmatch.fnmatch(name, pat):
                                return False
                    if args.include:
                        if name in include_nonglobs:
                            return True
                        for pat in include_globs:
                            if fnmatch.fnmatch(name, pat):
                                return True
                        return False
                    return True

                if os.path.isfile(path):
                    add_file(zf, path, base)
                else:
                    for root, dirs, files in os.walk(path):
                        for name in files:
                            if include_not_exclude(name):
                                p = os.path.join(root, name)
                                add_file(zf, p, base)
                        ixs = reversed([ix for ix, d in dirs if d in exclude_nonglobs])
                        for ix in ixs:
                            del dirs[ix]
                        
    if args.command == 'x':
        # todo extract globs and dirs, use --list

        with zipfile.ZipFile(args.zip) as zf:
            helper = Helper(zf)
            def find_list(sources):
                matched = set()
                for source in sources:
                    if '*' in source:
                        for item in helper.match(source):
                            matched.add(item)
                    else:
                        if helper.is_dir(source):
                            for item in helper.listdir(source):
                                matched.add(item)
                        else:
                            matched.add(helper.file(source))
                return matched

            if len(args.sources) > 0:
                matched = find_list(args.sources)
            elif args.list:
                matched = find_list(read_file_lines(args.list))
            elif args.stdin:
                matched = find_list(read_stdin_lines())
            else:
                matched = helper.filenames()
            
            matched = list(matched)
            matched.sort(key=lambda item: item[1])

            if args.output:
                output = path_to_list(args.output)
            else:
                output = path_to_list(os.getcwd())

            for filename_, filename in matched:
                path = path_to_list(filename)
                if args.strip:
                    path = path[args.strip:]
                    if len(path) == 0:
                        continue

                dest = os.path.join(*(output + path))

                if dest.endswith('/') or dest.endswith('\\'):
                    os.makedirs(dest.rstrip('/\\'), exist_ok=True)
                    continue

                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with zf.open(filename_, 'r') as fsrc:
                    with open(dest, 'wb') as fdst:
                        #pipe_file(fin, fout)
                        shutil.copyfileobj(fsrc, fdst)
                        if args.verbose:
                            print_utf8(dest)
                            #print(dest)
                    
    if args.command == 'l':
        # todo print size

        def get_depth(path):
            return len(re.split("[\\\\/]", path))

        dirnames = set()
        
        with zipfile.ZipFile(args.zip) as zf:
            for name in zf.namelist():
                if args.type == 'd':
                    dirname = os.path.dirname(name)
                    if args.depth == 0 or get_depth(dirname) <= args.depth:
                        dirnames.add(dirname)
                else:
                    if args.depth == 0 or get_depth(name) <= args.depth:
                        print_utf8(name)
        
        dirnames = list(dirnames)

        dirnames.sort()

        if args.type == 'd':
            for name in dirnames:
                print_utf8(name)

if __name__ == "__main__":
    main()