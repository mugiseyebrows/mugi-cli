import argparse
from . import parse_time_arg
from bashrange import expand_args
import random
import time

def randfloat(v1, v2):
    return random.random() * (v2 - v1) + v1

def main():
    example_text = """examples:
  pysleep 1m && taskkill 
  pysleep 10 20
  pysleep 60 --print 10
"""
    parser = argparse.ArgumentParser(prog='pysleep', description='sleeps for TIME seconds', epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p","--print", type=float, help="print reminding time")
    parser.add_argument("time", nargs='+')
    args = parser.parse_args(expand_args())
    #print(args); exit(0)
    times = [parse_time_arg(arg) for arg in args.time]
    
    if len(times) == 1:
        interval = times[0]
    elif len(times) == 2:
        interval = randfloat(*times)
    else:
        raise ValueError("time should be one or two numbers")
    
    if args.print is not None:
        step = args.print
    else:
        step = interval

    while interval > 0:
        step_ = min(step, interval)
        time.sleep(step_)
        interval -= step_
        if args.print is not None:
            print("{:.1f}".format(interval))
         
if __name__ == "__main__":
    main()