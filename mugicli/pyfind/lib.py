from .node import expr_to_pred
from .tok import T, TOK
from .action import ActionCallback
from .types import ExtraArgs, Exec
from .alg import walk_all

class Lib:
    def __init__(self, paths):
        self._paths = paths
        self._expr = []
        self._extraArgs = ExtraArgs(0, None)

    def iname(self, *names):
        self._expr.append(T(TOK.iname, '-iname', None))
        for name in names:
            self._expr.append(T(TOK.arg, name, None))
        return self

    def with_exts(self, *exts):
        expr = self._expr
        expr.append(T(TOK.iname, '-iname', None))
        for ext in exts:
            if not ext.startswith('.'):
                ext = '.' + ext
            expr.append(T(TOK.arg, '*' + ext, None))
        return self

    def type_dir(self):
        self._expr.extend([
            T(TOK.type, '-type', None),
            T(TOK.arg, 'd', None)
        ])
        return self
    
    def type_file(self):
        self._expr.extend([
            T(TOK.type, '-type', None),
            T(TOK.arg, 'f', None)
        ])
        return self

    def maxdepth(self, n):
        self._extraArgs.maxdepth = n
        return self

    def first(self, n):
        self._extraArgs.first = n
        return self
    
    def mtime(self, arg):
        self._expr.extend([
            T(TOK.mtime, '-mtime', None),
            T(TOK.arg, str(arg), arg)
        ])
        return self

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