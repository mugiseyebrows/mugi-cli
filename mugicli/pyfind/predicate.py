from ..shared import eprint
import datetime
import os
import fnmatch
import re

NOW = datetime.datetime.now()

def _getsize(path):
    return os.path.getsize(path)

def _getctime(path):
    return datetime.datetime.fromtimestamp(os.path.getctime(path))

def _getmtime(path):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path))

# =================== <Predicates>

def mmin(name, path, is_dir, arg, val):
    mtime = _getmtime(path)
    if mtime is None:
        return None
    total_min = (NOW - mtime).total_seconds() / 60
    #arg = float(arg)
    arg = val
    if arg < 0:
        return total_min < abs(arg)
    return total_min > arg

def iname(name, path, is_dir, arg, val):
    for pat in arg:
        if fnmatch.fnmatch(name, pat):
            return True
    return False

def name(name, path, is_dir, arg, val):
    for pat in arg:
        if fnmatch.fnmatchcase(name, pat):
            return True
    return False

def ipath(name, path, is_dir, arg, val):
    for pat in arg:
        if fnmatch.fnmatch(path, pat):
            return True
    return False

def path(name, path, is_dir, arg, val):
    for pat in arg:
        if fnmatch.fnmatchcase(path, pat):
            return True
    return False


def type(name, path, is_dir, arg, val):
    return is_dir == (arg == 'd')

def greater(d1, d2):
    if None in [d1, d2]:
        return None
    return d1 > d2

def newer(name, path, is_dir, arg, val):
    return greater(_getmtime(path), val)
    
def newermt(name, path, is_dir, arg, val):
    return greater(_getmtime(path), val)

def newerct(name, path, is_dir, arg, val):
    return greater(_getctime(path), val)

def _xtime(arg, val, xtime):
    if xtime is None:
        return None
    total_days = (NOW - xtime).total_seconds() / 60 / 60 / 24
    #arg = float(arg)
    arg = val
    if arg < 0:
        return total_days < abs(arg)
    return total_days > arg

def ctime(name, path, is_dir, arg, val):
    return _xtime(arg, val, _getctime(path))

def mtime(name, path, is_dir, arg, val):
    return _xtime(arg, val, _getmtime(path))

def _getmdate(path):
    d = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.datetime(d.year, d.month, d.day)

def mdate(name, path, is_dir, arg, val):
    d = _getmdate(path)
    #ds = [datetime.datetime.strptime(s, "%Y-%m-%d") for s in arg]
    ds = val
    if len(ds) == 1:
        return ds[0] <= d <= ds[0]
    return ds[0] <= d <= ds[1]

def size(name, path, is_dir, arg, val):
    if is_dir:
        return None
    #size_arg = cached_parse_size(arg)
    size_arg = val
    size_path = _getsize(path)
    if None in [size_arg, size_path]:
        return None
    if size_arg < 0:
        return size_path < abs(size_arg)
    return size_path > size_arg

def _xgrep(name, path, is_dir, arg, flags, bin):
    if is_dir:
        return None
    try:
        if bin:
            # todo buffered read for big files
            with open(path, 'rb') as f:
                data = f.read()
            arg = arg.encode("utf-8").decode('unicode_escape').encode('utf-8')
            return arg in data
        else:
            try:
                with open(path, encoding='utf-8') as f:
                    text = f.read()
                return re.search(arg, text, flags) is not None
            except UnicodeDecodeError as e:
                #print("UnicodeDecodeError", e, path)
                pass
            except UnicodeEncodeError as e:
                #print("UnicodeEncodeError", e)
                pass

    except Exception as e:
        eprint(e)
    return None

def grep(name, path, is_dir, arg, val):
    return _xgrep(name, path, is_dir, arg, 0, False)

def igrep(name, path, is_dir, arg, val):
    return _xgrep(name, path, is_dir, arg, re.IGNORECASE, False)

def bgrep(name, path, is_dir, arg, val):
    return _xgrep(name, path, is_dir, arg, 0, True)
