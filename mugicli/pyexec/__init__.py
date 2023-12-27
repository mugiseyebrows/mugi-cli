import sys
from ..shared import adjust_command, debug_print
from .split import exec_split, split_cmds
from .chain import to_chains, to_trains
from bashrange import expand_args

def print_help():
    print("""usage: pyexec commands

executes one or more commands conditionally

options:
  -h, --help  show this help message and exit

examples:
  pyexec "echo 1 && echo 2 || echo 3 && echo 4; pytrue && echo 5; pyfalse && echo 6"
  pyexec "echo 'some file.txt'; pycat 'some file.txt'"
  pyexec pytrue "&&" echo {1..3}

""")

def main():
    """
    Chain is conditionally connected sequence of commands, chains are independent and separated by semicolon.
    Train consists of one or many commands (car) that pipes output into next command

    |--------------chain--------------|   |------chain-------|
    echo 123 | pysed s,1,2 && echo 2345 ; pyfalse || echo 345
    |--------train-------|    |-train-|   |train|    |-train-|
    |--car--|  |---car---|    |--car--|   |-car-|    |--car--|
    """

    args = expand_args()
    if len(args) == 1 and args[0] in ['-h', '--help']:
        print_help()
        exit(0)
    if len(args) == 0:
        print_help()
        exit(0)
    
    if len(args) == 1:
        args = exec_split(args)
    
    cmds = list(split_cmds(args))
    debug_print("cmds", cmds)

    def pop_until(trains, op):
        while len(trains) > 0:
            train = trains.pop(0)
            if train == op:
                if len(trains) > 0:
                    return trains.pop(0)
                else:
                    return
    
    for chain in to_chains(cmds):
        #debug_print("chain", chain)
        trains = list(to_trains(chain))
        if len(trains) == 0:
            continue
        train = trains.pop(0)
        returncode = train.exec()
        while True:
            op = '&&' if returncode == 0 else '||'
            train = pop_until(trains, op)
            if train is None:
                break
            returncode = train.exec()
