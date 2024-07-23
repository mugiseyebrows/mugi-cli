import os
import datetime
from ..shared import eprint

def _unc_path(path):
    return '\\\\?\\' + path

def _getsize(path, try_unc = True):
    try:
        size = os.path.getsize(path)
        return size
    except FileNotFoundError as e:
        if try_unc:
            path = _unc_path(path)
            return _getsize(path, False)
        else:
            eprint(e)

def _getctime(path, try_unc = True):
    try:
        ctime = os.path.getctime(path)
        return datetime.datetime.fromtimestamp(ctime)
    except FileNotFoundError as e:
        if try_unc:
            path = _unc_path(path)
            return _getctime(path, False)
        else:
            eprint(e)

def _getmtime(path, try_unc = True):
    try:
        mtime = os.path.getmtime(path)
        return datetime.datetime.fromtimestamp(mtime)
    except FileNotFoundError as e:
        if try_unc:
            path = _unc_path(path)
            return _getmtime(path, False)
        else:
            eprint(e)
