from dataclasses import dataclass
from typing import Any
from ..shared import adjust_command, debug_print
import subprocess
import re

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

def to_chains(cmds):
    chain = []
    for e in cmds:
        if e == ';':
            yield chain
            chain = []
        else:
            chain.append(e)
    yield chain

class Train:
    def __init__(self, cmds):
        self._cars = [cmd for cmd in cmds if cmd != '|']

    def exec(self):
        cars = self._cars
        #if len(cars) == 1:
        if 0:
            car = cars[0]
            cmd, stdout_redir, stderr_redir = redicrects(car)
            cmd_ = adjust_command(cmd)
            stdout = None
            stderr = None
            
            if stdout_redir.file:
                mode = "ab" if stdout_redir.append else "wb"
                stdout = open(stdout_redir.file, mode)
            if stderr_redir.file:
                mode = "ab" if stderr_redir.append else "wb"
                stderr = open(stderr_redir.file, mode)

            if stdout_redir.join:
                stdout = stderr
            if stderr_redir.join:
                stderr = stdout
            debug_print("executing", cmd_, "stdout", stdout, "stderr", stderr)

            proc = subprocess.run(cmd_, stderr=stderr, stdout=stdout)
            return proc.returncode
        else:
            processes = []
            files = []
            for i, car in enumerate(reversed(cars)):
                cmd, stdout_redir, stderr_redir = redicrects(car)

                stdout = None
                stderr = None
                
                if stdout_redir.file:
                    mode = "ab" if stdout_redir.append else "wb"
                    stdout = open(stdout_redir.file, mode)
                if stderr_redir.file:
                    mode = "ab" if stderr_redir.append else "wb"
                    stderr = open(stderr_redir.file, mode)

                if stdout:
                    files.append(stdout)
                if stderr:
                    files.append(stderr)

                if stdout_redir.join:
                    stdout = stderr
                if stderr_redir.join:
                    stderr = stdout
                
                if i != len(cars) - 1:
                    stdin = subprocess.PIPE
                else:
                    stdin = None

                if len(processes) > 0:
                    stdout = processes[-1].stdin
                    
                cmd = adjust_command(cmd)
                debug_print("starting", cmd, "stdin", stdin, "stdout", stdout, "stderr", stderr)
                proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, stdin=stdin)
                processes.append(proc)

            #debug_print("processes communicate")
            for proc in reversed(processes):
                proc.communicate()
            #debug_print("processes wait")
            for proc in reversed(processes):
                proc.wait()
            #debug_print("closing files")
            for file in files:
                file.close()

            return processes[0].returncode

    def __repr__(self):
        return str(self._cars)

def to_trains(chain):
    train = []
    for e in chain:
        if e in ['||', '&&']:
            yield Train(train)
            yield e
            train = []
        else:
            train.append(e)
    yield Train(train)
