from bashrange import expand_args
import re
import argparse
import sys
from .shared import glob_paths_files
import io
import os

def conv(args):
    res = []
    for arg in args:
        m = re.match('-([0-9]+)', arg)
        if m:
            res.append('-n')
            res.append('{}'.format(m.group(1)))
        else:
            res.append(arg)
    return res

(
    MODE_HEAD,
    MODE_TAIL
) = range(2)

class ByteReader:
    def __init__(self, f: io.BufferedReader, mode, n, offset):
        self._f = f
        self._mode = mode
        self._n = n
        self._offset = offset
    def read(self):
        mode = self._mode
        f = self._f
        n = self._n
        seekable = f.seekable()
        fout = sys.stdout.buffer
        offset = self._offset
        if mode == MODE_HEAD:
            # skip offset bytes
            if seekable:
                fsize = f.seek(0, os.SEEK_END)
                if fsize <= offset:
                    return
                f.seek(offset)
            else:
                while True:
                    if offset == 0:
                        break
                    size = min(BUF_SIZE, offset)
                    chunk = f.read(size)
                    eof = len(chunk) < size
                    if eof:
                        return
                    offset -= size
            # read n bytes
            while True:
                size = min(BUF_SIZE, n)
                chunk = f.read(size)
                eof = len(chunk) < size
                fout.write(chunk)
                n -= size
                if n == 0 or eof:
                    break
        elif mode == MODE_TAIL:
            if offset != 0:
                raise ValueError("tail with offset is not implemented")
            if seekable:
                fsize = f.seek(0, os.SEEK_END)
                pos = min(n, fsize)
                f.seek(-pos, os.SEEK_END)
                while True:
                    chunk = f.read(BUF_SIZE)
                    fout.write(chunk)
                    eof = len(chunk) < BUF_SIZE
                    if eof:
                        break
            else:
                # todo stream implementation
                data = f.read()
                fout.write(data[-n:])

BUF_SIZE = 4096

class LineReader:

    def __init__(self, f: io.BufferedReader, mode, n, offset):
        self._f = f
        self._mode = mode
        self._n = n
        self._offset = offset

    def read(self):
        mode = self._mode
        f = self._f
        n = self._n
        seekable = f.seekable()
        last_line = b''
        fout = sys.stdout.buffer
        offset = self._offset
        if mode == MODE_HEAD:
            while True:
                chunk = f.read(BUF_SIZE)
                eof = len(chunk) < BUF_SIZE
                lines = chunk.splitlines(keepends=True)
                lines[0] = last_line + lines[0]
                last_line = lines.pop(-1)
                for line in lines:
                    if offset > 0:
                        offset -= 1
                    else:
                        n -= 1
                        fout.write(line)
                    if n == 0:
                        break
                if eof or n == 0:
                    break
            if n > 0:
                fout.write(last_line)
        elif mode == MODE_TAIL:
            if offset != 0:
                raise ValueError("tail with offset is not implemented")
            if seekable:
                size = f.seek(0, os.SEEK_END)
                prev_pos = size
                chunks: list[bytes] = []
                counts: list[int] = []
                ix = 0
                while True:
                    pos_offset = (ix + 1) * BUF_SIZE
                    if pos_offset > size:
                        pos_offset = size
                    pos = f.seek(-pos_offset, os.SEEK_END)
                    chunk_size = prev_pos - pos
                    chunk = f.read(chunk_size)
                    chunks.append(chunk)
                    counts.append(chunk.count(b'\n'))
                    prev_pos = pos
                    ix += 1
                    if sum(counts) >= n:
                        break
                    if pos == 0:
                        break
                data = b''.join(reversed(chunks))
                lines = data.splitlines(keepends=True)
                fout.write(b''.join(lines[-n:]))
            else:
                # todo stream implementation
                data = f.read()
                lines = data.splitlines(keepends=True)
                fout.write(b''.join(lines[-n:]))

def x_main(mode):
    args = expand_args()
    args = conv(args)
    if mode == MODE_HEAD:
        description = 'outputs first n lines (or bytes) of file or stdin'
    else:
        description = 'outputs last n lines (or bytes) of file or stdin'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-n', '--lines', type=int, help='number of lines')
    parser.add_argument('-c', '--bytes', type=int, help='number of bytes')
    if mode == MODE_HEAD:
        parser.add_argument('-o', '--offset', type=int, default=0)
    parser.add_argument('-q', '--quiet', action='store_true', help='do not print header')
    parser.add_argument('file', nargs='*')
    args = parser.parse_args(args)
    #print(args); exit(0)

    if mode == MODE_TAIL:
        args.offset = 0

    if args.lines is None and args.bytes is None:
        raise ValueError("pass -n or -c")
    
    if args.lines is not None and args.bytes is not None:
        raise ValueError("pass only one: -n or -c")

    if len(args.file) > 0:
        # files mode
        files = glob_paths_files(args.file)
        print_header = len(files) > 1 and not args.quiet
        for p in files:
            if print_header:
                pass
            with open(p, 'rb') as f:
                if args.bytes is None:
                    reader = LineReader(f, mode, args.lines, args.offset)
                else:
                    reader = ByteReader(f, mode, args.bytes, args.offset)
                reader.read()
    else:
        # stdin mode
        if args.bytes is None:
            reader = LineReader(sys.stdin.buffer, mode, args.lines, args.offset)
        else:
            reader = ByteReader(sys.stdin.buffer, mode, args.bytes, args.offset)
        reader.read()

def head_main():
    return x_main(MODE_HEAD)

def tail_main():
    return x_main(MODE_TAIL)