import subprocess
import time
import sys
from .shared import adjust_command, eprint, run
import textwrap
from bashrange import expand_args
import asyncio

try:
    import psutil
except ImportError:
    pass

def print_help():
    print("""
usage: pytime program [-h] [--help] [-s SECONDS] [--stat SECONDS]

optional arguments:
  -s, --stat SECONDS   measure cpu and memory usage, 
                       take samples with interval of SECONDS

measures execution time of application
""")

class ProcCache:
    def __init__(self, process):
        self._process = process
        self._cache = dict()

    def process_and_children(self):
        res = [self._process]        
        for child in self._process.children():
            ok = False
            if child.pid in self._cache:
                child_ = self._cache[child.pid]
                if child_.is_running():
                    res.append(child_)
                    ok = True
            if not ok:
                self._cache[child.pid] = child
                res.append(child)
        return res

async def memory_and_usage(pid, stat_sample_rate):
    process = psutil.Process(pid)
    vms = []
    rss = []
    cpu = []
    
    #await asyncio.sleep(stat_sample_rate)

    procCache = ProcCache(process)

    while process.is_running():
        rss_ = 0
        vms_ = 0
        cpu_ = sum([proc.cpu_percent() for proc in procCache.process_and_children()])

        for item in [process] + process.children():
            try:
                info = item.memory_info()
                rss_ += info.rss
                vms_ += info.vms
            except psutil.NoSuchProcess:
                pass
        rss.append(rss_)
        vms.append(vms_)
        cpu.append(cpu_ / psutil.cpu_count())
        #print("cpu_ / psutil.cpu_count()", cpu_ / psutil.cpu_count(), "psutil.cpu_count()", psutil.cpu_count())
        #print("cpu_", cpu_)
        await asyncio.sleep(stat_sample_rate)
    return rss, vms, cpu

def min_max_med_avg(items):
    items_ = sorted(items)
    med = items_[int(len(items_) / 2)]
    avg = sum(items_) / len(items_)
    return items_[0], items_[-1], med, avg

def mem_stat(name, items):
    stat = [v / 1024 / 1024 for v in min_max_med_avg(items)]
    return "{} min {:.1f} max {:.1f} med {:.1f} avg {:.1f}".format(name, *stat)

def cpu_stat(name, items):
    stat = min_max_med_avg(items)
    return "{} min {:.1f} max {:.1f} med {:.1f} avg {:.1f}".format(name, *stat)

async def async_main():
    args = expand_args()

    stat_sample_rate = None

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
            else:
                cmd = args[i:]
                break

    cmd = adjust_command(cmd)

    #print("cmd", cmd, "args", args)
    t1 = time.time()
    process = await asyncio.create_subprocess_exec(*cmd)
    #print(process)
    if stat_sample_rate is not None:
        rss, vms, cpu = await memory_and_usage(process.pid, stat_sample_rate)
        print(mem_stat("rss(Mb)", rss))
        print(mem_stat("vms(Mb)", vms))
        print(cpu_stat("cpu(%)", cpu))
    await process.wait()
    t2 = time.time()
    eprint("{:.3f}s".format(t2 - t1))

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()