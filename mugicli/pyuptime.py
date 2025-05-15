import datetime
import argparse

HAS_PSUTIL = False
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    pass

def todhms(td: datetime.timedelta):
    s = td.total_seconds()
    d = int(s // (24 * 3600))
    s -= d * 24 * 3600
    h = int(s // 3600)
    s -= h * 3600
    m = int(s // 60)
    s -= m * 60
    return d,h,m,int(s)

def main():

    parser = argparse.ArgumentParser(description='prints uptime information')
    args = parser.parse_args()

    if not HAS_PSUTIL:
        print("pyuptime requires psutil: pip install psutil")
        return
    
    boot_date = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    d,h,m,s = todhms(now - boot_date)

    print(f"booted {boot_date}")
    print(f"uptime {d} days and {h:02d}:{m:02d}:{s:02d}")

if __name__ == "__main__":
    main()
