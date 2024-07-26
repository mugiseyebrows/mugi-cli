from .node import expr_to_pred
from .tok import T, TOK
from .action import ActionCallback
from .types import ExtraArgs, Exec
from .alg import walk_all
import datetime

def with_dot(ext):
    if not ext.startswith('.'):
        return '.' + ext
    return ext

def ext_to_wild(ext):
    return '*' + with_dot(ext)

class Lib:
    def __init__(self, paths):
        self._paths = paths
        self._expr = []
        self._extraArgs = ExtraArgs(0, None)

    def name(self, *pats):
        return self._nargs(TOK.name, '-name', pats)

    def iname(self, *pats):
        return self._nargs(TOK.iname, '-iname', pats)
    
    def path(self, *pats):
        return self._nargs(TOK.path, '-path', pats)
    
    def ipath(self, *pats):
        return self._nargs(TOK.ipath, '-ipath', pats)

    def with_exts(self, *exts):
        tokens = [T(TOK.arg, ext_to_wild(ext), None) for ext in exts]
        return self._nargs(TOK.iname, '-iname', tokens)

    def type_dir(self):
        return self._onearg(TOK.type, '-type', 'd', None)
    
    def type_file(self):
        return self._onearg(TOK.type, '-type', 'f', None)

    def maxdepth(self, n):
        self._extraArgs.maxdepth = n
        return self

    def first(self, n):
        self._extraArgs.first = n
        return self
    
    def _nargs(self, type, pred_str, tokens):
        if len(tokens) > 0 and isinstance(tokens[0], str):
            tokens = [T(TOK.arg, arg) for arg in tokens]
        self._expr.extend([T(type, pred_str, None)] + tokens)
        return self

    def _onearg(self, type, pred_str, arg, val = None):
        self._expr.extend([
            T(type, pred_str, None),
            T(TOK.arg, str(arg), val)
        ])
        return self

    def mtime(self, arg):
        return self._onearg(TOK.mtime, '-mtime', arg, arg)
    
    def ctime(self, arg):
        return self._onearg(TOK.ctime, '-ctime', arg, arg)
    
    def grep(self, arg):
        return self._onearg(TOK.grep, '-grep', arg)

    def igrep(self, arg):
        return self._onearg(TOK.igrep, '-igrep', arg)
    
    def bgrep(self, arg):
        return self._onearg(TOK.bgrep, '-bgrep', arg)
    
    def mmin(self, arg: float):
        return self._onearg(TOK.mmin, '-mmin', arg, arg)
    
    def cmin(self, arg: float):
        return self._onearg(TOK.cmin, '-cmin', arg, arg)
    
    def newer(self, arg: str):
        return self._onearg(TOK.newer, '-newer', arg, arg)
    
    def newermt(self, arg: datetime.datetime):
        return self._onearg(TOK.newermt, '-newermt', arg, arg)
    
    def newerct(self, arg: datetime.datetime):
        return self._onearg(TOK.newerct, '-newerct', arg, arg)

    async def run_async(self, callback: Exec):
        action = ActionCallback(callback)
        tree, pred = expr_to_pred(self._expr)
        walk_all(self._paths, pred, action, self._extraArgs)
        await action.wait()

    def run(self, callback: Exec):
        action = ActionCallback(callback)
        tree, pred = expr_to_pred(self._expr)
        walk_all(self._paths, pred, action, self._extraArgs)

def find(*paths):
    lib = Lib(paths)
    return lib