try:
    import win32api
except ImportError:
    pass
import datetime
import argparse

def main():

    parser = argparse.ArgumentParser(description='prints uptime information')
    parser.add_argument('-p', '--pretty', action='store_true', help='pretty print')
    args = parser.parse_args()

    tickCount = win32api.GetTickCount()
    delta = datetime.timedelta(milliseconds=tickCount)
    s = delta.seconds
    h = s // 3600
    s -= h * 3600
    m = s // 60
    s -= m * 60

    if args.pretty:
        res = []
        if delta.days > 0:
            res.append("{:d} days".format(delta.days))
        res.append("{:d} hours {:d} minutes {:d} seconds".format(h, m, s))
        print(" ".join(res))
    else:
        print("{:02d}:{:02d}:{:02d}:{:02d}".format(delta.days, h, m, s))

if __name__ == "__main__":
    main()
