import subprocess
import time
import sys
from .shared import adjust_command, eprint, run
import textwrap
from bashrange import expand_args
import asyncio
import json
import math

try:
    import psutil
except ImportError:
    pass

def print_help():
    print("""
usage: pytime program [-h] [--help] [-s SECONDS] [--stat SECONDS] [-p PATH] [--path PATH]

runs program and measures execution time, memory and cpu usage

optional arguments:
  -s SECONDS, --stat SECONDS   measure cpu and memory usage, 
                               take samples with interval of SECONDS
  -p PATH, --path PATH         save cpu and memory stats in file PATH
  -o, --online                 show stat while executing program
""")

class ProcTree:
    def __init__(self, process):
        self._process = process
        self._cache = dict()

    def tree(self):
        queue = [self._process]
        yield self._process
        while len(queue) > 0:
            parent = queue.pop(0)
            try:
                for child in parent.children():
                    ok = False
                    if child.pid in self._cache:
                        child_ = self._cache[child.pid]
                        if child_.is_running():
                            yield child_
                            ok = True
                    if not ok:
                        self._cache[child.pid] = child
                        yield child
                    queue.append(child)
            except psutil.NoSuchProcess:
                pass

async def memory_and_usage(pid, stat_sample_rate, show_online_stat):
    process = psutil.Process(pid)
    vms = []
    rss = []
    cpu = []
    
    tree = ProcTree(process)

    while process.is_running():
        rss_ = 0
        vms_ = 0
        cpu_ = sum([proc.cpu_percent() for proc in tree.tree()]) / psutil.cpu_count()

        for proc in tree.tree():
            try:
                info = proc.memory_info()
                rss_ += info.rss
                vms_ += info.vms
            except psutil.NoSuchProcess:
                pass
        rss.append(rss_)
        vms.append(vms_)
        cpu.append(cpu_)
        if show_online_stat:
            eprint(online_stat(rss_, vms_, cpu_))
        await asyncio.sleep(stat_sample_rate)
    return rss, vms, cpu

def linterp(items, ix):
    ix1 = math.floor(ix)
    ix2 = ix1 + 1
    d = ix - ix1
    if ix2 >= len(items):
        return items[-1]
    if ix1 < 0:
        return items[0]
    v1 = items[ix1]
    v2 = items[ix2]
    return (v2 - v1) * d + v1

def min_max_med_avg_q90(items):
    items_ = sorted(items)
    med = items_[int(len(items_) / 2)]
    avg = sum(items_) / len(items_)

    q = (1 - 0.9) / 2
    ix1 = len(items) * q
    ix2 = len(items) - 1 - len(items) * q
    
    q90a = linterp(items_, ix1)
    q90b = linterp(items_, ix2)

    return items_[0], items_[-1], med, avg, q90a, q90b

def mem_stat(name, items):
    stat = [v / 1024 / 1024 for v in min_max_med_avg_q90(items)]
    return "{} min {:.1f} max {:.1f} med {:.1f} avg {:.1f} q90 {:.1f} {:.1f}".format(name, *stat)

def cpu_stat(name, items):
    stat = min_max_med_avg_q90(items)
    return "{} min {:.1f} max {:.1f} med {:.1f} avg {:.1f} q90 {:.1f} {:.1f}".format(name, *stat)

def online_stat(rss, vms, cpu):
    return "rss(Mb) {:.1f} vms(Mb) {:.1f} cpu(%) {:.1f}".format(rss / 1024 / 1024, vms / 1024 / 1024, cpu)

async def async_main():
    args = expand_args()

    stat_sample_rate = None

    stat_path = None

    show_online_stat = False

    if '--' in args:
        cmd = args[args.index('--') + 1:]
    else:
        i = 0
        while True:
            if args[i] in ['-h', '--help']:
                print_help()
                exit(0)
            elif args[i] in ['-s', '--stat']:
                stat_sample_rate = float(args[i+1])
                i += 2
            elif args[i] in ['-p', '--path']:
                stat_path = args[i+1]
                i += 2
            elif args[i] in ['-o', '--online']:
                show_online_stat = True
                i += 1
            else:
                cmd = args[i:]
                break

    cmd = adjust_command(cmd)

    #print("cmd", cmd, "args", args)
    t1 = time.time()
    process = await asyncio.create_subprocess_exec(*cmd)
    #print(process)
    if stat_sample_rate is not None:
        rss, vms, cpu = await memory_and_usage(process.pid, stat_sample_rate, show_online_stat)
        eprint(mem_stat("rss(Mb)", rss))
        eprint(mem_stat("vms(Mb)", vms))
        eprint(cpu_stat("cpu(%)", cpu))
        if stat_path is not None:
            with open(stat_path, "w", encoding='utf-8') as f:
                json.dump({"rss": rss, "vms": vms, "cpu": cpu}, f)
    await process.wait()
    t2 = time.time()
    eprint("{:.3f}s".format(t2 - t1))

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()