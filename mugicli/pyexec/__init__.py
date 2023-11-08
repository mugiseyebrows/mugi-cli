import sys
from ..shared import adjust_command, debug_print
import subprocess
import re
from .split import exec_split, split_cmds

def to_chains(cmds):
    chain = []
    for e in cmds:
        if e == ';':
            yield chain
            chain = []
        else:
            chain.append(e)
    yield chain

def print_help():
    print("""usage: pyexec commands

executes one or more commands conditionally

options:
  -h, --help  show this help message and exit
          
examples:
  pyexec "echo 1 && echo 2 || echo 3 && echo 4; pytrue && echo 5; pyfalse && echo 6"
  pyexec "echo 'some file.txt'; pycat 'some file.txt'"

""")

# todo pipe stdout to file or process

from dataclasses import dataclass
from typing import Any

@dataclass
class Redir:
    file: Any = None
    append: bool = False
    join: bool = False
    
def redicrects(cmd):
    cmd_ = cmd[:]
    stderr = Redir()
    stdout = Redir()
    if len(cmd_) > 0:
        if cmd_[-1] == '2>&1':
            stderr.join = True
            cmd_.pop(-1)
        elif cmd_[-1] == '1>&2':
            stdout.join = True
            cmd_.pop(-1)

    while len(cmd_) > 1:
        ok = False
        if cmd_[-2] in ['1>', '>']:
            stdout.file = cmd_[-1]
            stdout.append = False
            ok = True
        elif cmd_[-2] in ['1>>', '>>']:
            stdout.file = cmd_[-1]
            stdout.append = True
            ok = True
        elif cmd_[-2] == '2>':
            stderr.file = cmd_[-1]
            stderr.append = False
            ok = True
        elif cmd_[-2] == '2>>':
            stderr.file = cmd_[-1]
            stderr.append = True
            ok = True
        if ok:
            cmd_.pop(-1)
            cmd_.pop(-1)
        else:
            break
    return cmd_, stdout, stderr

def main():
    args = sys.argv[1:]
    if len(args) == 1 and args[0] in ['-h', '--help']:
        print_help()
        exit(0)
    if len(args) == 0:
        print_help()
        exit(0)
    
    args = exec_split(args)
    cmds = list(split_cmds(args))
    debug_print("cmds", cmds)
    
    for chain in to_chains(cmds):
        debug_print("chain", chain)
        returncode = 0
        for cmd in chain:
            if cmd == '&&':
                if returncode != 0:
                    debug_print("&& returncode != 0, skip")
                    break
            elif cmd == '||':
                if returncode == 0:
                    debug_print("|| returncode == 0, skip")
                    break
            else:
                if cmd == []:
                    debug_print('cmd == []')
                    continue
                cmd_, stdout_redir, stderr_redir = redicrects(cmd)
                #print(cmd_, stdout, stderr)

                cmd_ = adjust_command(cmd_)
                stdout = None
                stderr = None
                
                if stdout_redir.file:
                    mode = "ab" if stdout_redir.append else "wb"
                    stdout = open(stdout_redir.file, mode)
                if stderr_redir.file:
                    mode = "ab" if stderr_redir.append else "wb"
                    stderr = open(stderr_redir.file, mode)

                # stdout.join is 1>&2
                if stdout_redir.join:
                    stdout = stderr
                if stderr_redir.join:
                    stderr = stdout
                debug_print("executing", cmd_, "stdout", stdout, "stderr", stderr)
                proc = subprocess.run(cmd_, stderr=stderr, stdout=stdout)
                if stdout:
                    stdout.close()
                if stderr:
                    stderr.close()
                returncode = proc.returncode
                debug_print("returncode", returncode)

