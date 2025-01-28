import io
from functools import partial
import tempfile
import argparse
from bashrange import expand_args
from .shared import glob_paths_files, debug_print
import sys
import math

BLOCK_SIZE = 65536

#BLOCK_SIZE = 1024

def read_head_lines(f: io.TextIOWrapper, num, seekable) -> bytes:
    # todo \r\n
    blocks = []
    nlcount = 0
    for block in iter(partial(f.read, BLOCK_SIZE), b''):
        if block == b'':
            break
        nlcount += block.count(b'\n')
        blocks.append(block)
        if nlcount >= num:
            break
    return b'\n'.join(b''.join(blocks).split(b'\n')[:num]) + b'\n'

"""
def trim_first_block(blocks):
    try:
        block = blocks[0]
        p = block.index(b'\n')
        blocks[0] = block[p+1:]
    except ValueError:
        pass
"""

def tail_lines(blocks, num):
    return b'\n'.join(b''.join(blocks).split(b'\n')[-num:]) + b'\n'

def read_tail_lines(f: io.TextIOWrapper, num, seekable) -> bytes:
    # todo \r\n
    if seekable:
        blocks = []
        FROM_END = 2
        f.seek(0, FROM_END)
        filesize = f.tell()
        n = int(math.ceil(filesize / BLOCK_SIZE))
        #print("n", n)
        nlcount = 0
        for i in range(n):
            if i == n-1:
                block_size = filesize - (n - 1) * BLOCK_SIZE
            else:
                block_size = BLOCK_SIZE
            pos = filesize - (len(blocks) + 1) * BLOCK_SIZE
            if pos < 0:
                pos = 0
            f.seek(pos)
            #print("f.tell()", f.tell())
            block = f.read(block_size)
            blocks.insert(0, block)
            nlcount += block.count(b'\n')            
            if nlcount >= num:
                break
        #trim_first_block(blocks)
        return tail_lines(blocks, num)
    else:
        blocks = []
        nlcount = 0
        for block in iter(partial(f.read, BLOCK_SIZE), b''):
            if block == b'':
                break
            blocks.append(block)
            #debug_print("read block", len(blocks))
            nlcount += block.count(b'\n')
            if nlcount > num:
                count = blocks[0].count(b'\n')
                if nlcount - count >= num:
                    #debug_print("drop block", len(blocks))
                    blocks.pop(0)
                    nlcount -= count
                else:
                    pass
                    #debug_print("cannot drop block", len(blocks))
        #trim_first_block(blocks)
        return tail_lines(blocks, num)

def read_head_chars(f, num, seekable):
    return f.read(num)

def read_tail_chars(f, num, seekable):
    if seekable:
        FROM_END = 2
        f.seek(0, FROM_END)
        filesize = f.tell()
        pos = filesize - num
        if pos < 0:
            pos = 0
        f.seek(pos)
        return f.read(num)
    else:
        blocks = []
        for block in iter(partial(f.read, BLOCK_SIZE), b''):
            if block == b'':
                break
            blocks.append(block)
            if len(blocks) > 1:
                tail_size = sum([len(block) for block in blocks[1:]])
                if tail_size > num:
                    blocks.pop(0)
        return b''.join(blocks)[-num:]
        
def main(read_lines, read_chars):

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=int)
    parser.add_argument('-n', type=int)
    parser.add_argument('path', nargs='*')

    args = parser.parse_args(expand_args())

    if len(args.path) > 0:
        files = glob_paths_files(args.path)

    if args.c:
        n = args.c
        if len(args.path) > 0:
            for file in files:
                with open(file, 'rb') as f:
                    data = read_chars(f, n, True)
                    sys.stdout.buffer.write(data)
        else:
            data = read_chars(sys.stdin.buffer, n, False)
            sys.stdout.buffer.write(data)
    else:
        n = args.n
        if n is None:
            n = 10
        if len(args.path) > 0:
            # files 
            for file in files:
                with open(file, 'rb') as f:
                    data = read_lines(f, n, True)
                    sys.stdout.buffer.write(data)
        else:
            # stdin
            data = read_lines(sys.stdin.buffer, n, False)
            sys.stdout.buffer.write(data)