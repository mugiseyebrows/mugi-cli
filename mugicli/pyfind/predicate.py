from ..shared import eprint
import datetime
import os
import fnmatch
import re
import zipfile
from .types import AddressRange, FloatRange
from .shared import _getmtime, _getctime, _getsize

try:
    import xlrd
    from xlrd.book import Book
except ImportError:
    pass

NOW = datetime.datetime.now()

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

def mdate(name, path, is_dir, arg, val):
    d = _getmtime(path).date()
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

def _xgrep(name, path, is_dir, arg, flags, bin, try_unc = True):
    if is_dir:
        return None
    try:
        if bin:
            # todo buffered read for big files
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                arg = arg.encode("utf-8").decode('unicode_escape').encode('utf-8')
                return arg in data
            except FileNotFoundError as e:
                if try_unc:
                    return _xgrep(name, path, is_dir, arg, flags, bin, False)
                else:
                    eprint(e)
        else:
            try:
                with open(path, encoding='utf-8') as f:
                    text = f.read()
                return re.search(arg, text, flags) is not None
            except FileNotFoundError as e:
                if try_unc:
                    return _xgrep(name, path, is_dir, arg, flags, bin, False)
                else:
                    eprint(e)
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

def cpptmp(name, path, is_dir, arg, val):
    if is_dir:
        return False
    if os.path.splitext(name)[1].lower() in ['.o', '.obj']:
        return True
    if re.match('^ui_.*[.]h$', name):
        return True
    if re.match('^(qrc|moc)_.*[.]cpp$', name):
        return True
    if name.split(".")[0] in ['object_script', 'Makefile']:
        return True
    return False

def gitdir(name, path, is_dir, arg, val):
    if not is_dir:
        return False
    return os.path.isdir(os.path.join(path, '.git'))

def xlgrep(name, path, is_dir, arg, val):
    if is_dir:
        return False
    if os.path.splitext(name)[1].lower() not in ['.xls']:
        return False
    rngs = [v for v in val if isinstance(v, AddressRange)]
    txts = [v.lower() for v in val if isinstance(v, str)]
    ints = [v for v in val if isinstance(v, int)]
    floats = [v for v in val if isinstance(v, float)]
    float_ranges = [v for v in val if isinstance(v, FloatRange)]

    try:
        book: Book = xlrd.open_workbook(path)
    except xlrd.biffh.XLRDError:
        return False
    
    for i in range(book.nsheets):
        sh = book.sheet_by_index(i)
        # todo whole sheet if no range specified
        for rng in rngs:
            r1, c1, r2, c2 = rng
            #print(r1, c1, r2, c2)
            r2 = min(r2, sh.nrows)
            c2 = min(c2, sh.ncols)
            #print(r1, c1, r2, c2)
            for r in range(r1, r2+1):
                for c in range(c1, c2+1):
                    rowx = r - 1
                    colx = c - 1
                    v = sh.cell_value(rowx, colx)
                    if isinstance(v, (int, float)):
                        if v in ints:
                            return True
                        for f in floats + ints:
                            if abs(f - v) < 1e-4:
                                return True
                        for fr in float_ranges:
                            v1, v2 = fr
                            if v1 <= v <= v2:
                                return True
                    elif isinstance(v, str):
                        for t in txts:
                            if t in v.lower():
                                return True
                                
    return False

def docgrep(name, path, is_dir, arg, val):
    if is_dir:
        return False
    if os.path.splitext(name)[1].lower() not in ['.odt', '.ods']:
        return False
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            with z.open(info) as f:
                data = f.read()
                try:
                    text = data.decode('utf-8')
                    m = re.search(arg, text)
                    if m:
                        return True
                except UnicodeDecodeError:
                    pass
    return False