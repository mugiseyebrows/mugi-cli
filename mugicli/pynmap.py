import argparse
import asyncio
from sqlite3 import Time
from bashrange import expand_args
import re
from itertools import product

semaphore = asyncio.Semaphore(5000)

async def test_port(host, port, timeout):
    #print("host port", host, port)
    async with semaphore:
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout = timeout)
            return [host, port, True]
        except asyncio.exceptions.CancelledError as e:
            return [host, port, False]
        except asyncio.exceptions.TimeoutError as e:
            return [host, port, False]
        except PermissionError as e:
            #print(host, port)
            return [host, port, False]
        except OSError as e:
            print("OSError", host, port, e)
            return [host, port, False]
    
def ordered_uniq(vs):
    res = []
    for v in vs:
        if v not in res:
            res.append(v)
    return res

async def async_main():
    EXAMPLE_TEXT = """examples:
  pynmap 192.168.0.1-100 -p 80,8080
  pynmap 192.168.0.1/24 -p 1000-2000
"""

    parser = argparse.ArgumentParser(prog="", description="", epilog=EXAMPLE_TEXT, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", "--ports", nargs="+", help="ports to scan")
    parser.add_argument("-t", "--timeout", type=float, default=1, help="timeout for connection")
    parser.add_argument("ips", nargs="+", help="ips to scan")
    args = parser.parse_args(expand_args())
    #print(args); exit(0)

    ports = []
    if args.ports is None or args.ports == ['-']:
        ports = list(range(1, 2 ** 16))
    else:
        for arg in args.ports:
            for item in arg.split(","):
                try:
                    if "-" in item:
                        begin, end = [int(v) for v in item.split("-")]
                        ports += list(range(begin, end + 1))
                    else:
                        ports.append(int(item))
                except:
                    pass

    #print(ports); exit(0)

    def to_range(s):
        c = s.split("-")
        if len(c) == 1:
            return [int(c[0])]
        elif len(c) == 2:
            return list(range(int(c[0]), int(c[1])+1))

    def to_ip(vs):
        return ".".join([str(v) for v in vs])

    def masked(index, octet, mask):
        mask_ = mask - index * 8
        if mask_ >= 8:
            return [octet]
        if mask_ <= 0:
            return list(range(256))
        octet_ = octet & (255 ^ (2 ** (8 - mask_) - 1))
        return [octet_ | v for v in range(2 ** (8 - mask_))]

    ips = []
    
    for arg in args.ips:
        m = re.match("^([0-9-]+)\\.([0-9-]+)\\.([0-9-]+)\\.([0-9-]+)$", arg)
        if m:
            pattern = [to_range(m.group(i)) for i in range(1,5)]
            ips += [to_ip(ip) for ip in product(*pattern)]
            continue
        m = re.match("^([0-9]+)\\.([0-9]+)\\.([0-9]+)\\.([0-9]+)[//]([0-9]+)$", arg)
        if m:
            mask = int(m.group(5))
            octets = [int(m.group(i)) for i in range(1,5)]
            pattern = [masked(i, octet, mask) for i, octet in enumerate(octets)]
            ips += [to_ip(ip) for ip in product(*pattern)]
            continue
        raise ValueError("invalid ip range {}".format(arg))
    
    tests = [test_port(ip, port, args.timeout) for ip, port in product(ips, ports)]

    res = await asyncio.gather(*tests)
    for host, port, ok in res:
        if ok:
            print("{}:{}".format(host, port))

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())

if __name__ == "__main__":
    main()