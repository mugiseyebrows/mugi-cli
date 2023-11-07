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
                cmd_ = adjust_command(cmd)
                debug_print("executing", cmd_)
                proc = subprocess.run(cmd_)
                returncode = proc.returncode
                debug_print("returncode", returncode)

