import argparse
import os
import datetime
import sys
import re
from .shared import eprint, glob_paths_dirs, has_magic, run, print_utf8
import sys
from dataclasses import dataclass
from itertools import count
import subprocess
import shutil
import fnmatch
from . import parse_size

try:
    import dateutil.parser
except ImportError as e:
    eprint("{}, -newermt -newerct is limited to yyyy-mm-dd format".format(str(e)))
    def parse_date(value):
        m = re.match('([0-9]{4})-([0-9]{2})-([0-9]{2})', value)
        if m:
            year = int(m.group(1))
            month = int(m.group(2))
            day = int(m.group(3))
            return datetime.datetime(year, month, day)
    class dateutil:
        class parser:
            parse = parse_date

class Tok:
    (
        und,
        op_par,
        cl_par,
        not_,
        and_,
        or_,
        mmin,
        iname,
        name,
        type,
        f,
        d,
        newer,
        newermt,
        newerct,
        arg,
        path,
        ipath,
        mtime,
        ctime,
        size,
        exec,
        delete,
        semicolon,
        pathbind,
        icont,
        cont,
        bcont,
        maxdepth,
        cdup,
        first,
        last,
    ) = range(32)
    
m = {
    "(": Tok.op_par,
    ")": Tok.cl_par,
    "!": Tok.not_,
    "-not": Tok.not_,
    "-a": Tok.and_,
    "-and": Tok.and_,
    "-o": Tok.or_,
    "-or": Tok.or_,
    "-mmin": Tok.mmin,
    "-iname": Tok.iname,
    "-name": Tok.name,
    "-type": Tok.type,
    "f": Tok.f,
    "d": Tok.d,
    "-newer": Tok.newer,
    "-newermt": Tok.newermt,
    "-newerct": Tok.newerct,
    "-mtime": Tok.mtime,
    "-ctime": Tok.ctime,
    "-size": Tok.size,
    "-exec": Tok.exec,
    "-delete": Tok.delete,
    ";": Tok.semicolon,
    "{}": Tok.pathbind,
    "-icont": Tok.icont,
    "-cont": Tok.cont,
    "-bcont": Tok.bcont,
    "-path": Tok.path,
    "-ipath": Tok.ipath,
    "-maxdepth": Tok.maxdepth,
    "-cdup": Tok.cdup,
    "-first": Tok.first,
    "-last": Tok.last,
}

inv_m = {v:k for k,v in m.items()}

@dataclass
class T:
    type: int
    cont: str

tok_pred = [Tok.mmin, Tok.iname, Tok.name, Tok.type, Tok.newer, 
    Tok.newerct, Tok.newermt, Tok.mtime, Tok.ctime,  Tok.size, Tok.cont, Tok.icont, Tok.bcont, Tok.path, Tok.ipath]

def cdup_path(path, cdup):
    for i in range(cdup):
        path = os.path.dirname(path)
    return path

def split_list(vs, sep):
    res = []
    for v in vs:
        if v == sep:
            yield res
            res = []
        else:
            res.append(v)
    yield res
    res = []

class ActionExec:
    def __init__(self, tokens, cdup):
        self._tokens = tokens
        self._cdup = cdup

    def exec(self, root, name, path, is_dir):
        path = cdup_path(path, self._cdup)
        exprs = [t.cont.replace('{}', path) for t in self._tokens]
        for expr in split_list(exprs, '&&'):
            run(expr)

class ActionDelete:

    def __init__(self, cdup):
        self._cdup = cdup

    def exec(self, root, name, path, is_dir):
        path = cdup_path(path, self._cdup)
        if is_dir:
            eprint("Removing directory {}".format(path))
            shutil.rmtree(path)
        else:
            eprint("Removing file {}".format(path))
            os.remove(path)


class ActionPrint:

    def __init__(self, cdup):
        self._cdup = cdup

    def exec(self, root, name, path, is_dir):
        path = cdup_path(path, self._cdup)
        if os.path.isabs(root):
            print_utf8(path)
        else:
            print_utf8(os.path.relpath(path, os.getcwd()))

def index_of_token(tokens, type):
    for i, tok in enumerate(tokens):
        if tok.type == type:
            return i

@dataclass
class ExtraArgs:
    maxdepth: int
    first: int
    last: int

def pop_named_token_and_value(tokens, t):
    ix = index_of_token(tokens, t)
    if ix is None:
        return None
    if ix is not None:
        token_key = tokens.pop(ix)
        token_value = tokens.pop(ix)
        return token_value.cont

def to_int(v):
    if v is None:
        return v
    return int(v)

def to_int_or_zero(v):
    if v is None:
        return 0
    return int(v)

def parse_args(args = None):
    if args is None:
        args = sys.argv[1:]
    tokens = [T(m[t], t) if t in m else T(Tok.und, t) for t in args]
    for i, tok in enumerate(tokens):
        if tok.type in tok_pred:
            token = tokens[i+1]
            tokens[i+1] = T(Tok.arg, token.cont)

    """
    maxdepth = 0
    ix_maxdepth = index_of_token(tokens, Tok.maxdepth)
    if ix_maxdepth is not None:
        tokens.pop(ix_maxdepth)
        token = tokens.pop(ix_maxdepth)
        maxdepth = int(token.cont)
    """

    maxdepth = to_int_or_zero(pop_named_token_and_value(tokens, Tok.maxdepth))
    
    first = to_int(pop_named_token_and_value(tokens, Tok.first))

    last = to_int(pop_named_token_and_value(tokens, Tok.last))
    
    """
    cdup = 0
    ix = index_of_token(tokens, Tok.cdup)
    if ix is not None:
        tokens.pop(ix)
        token = tokens.pop(ix)
        cdup = int(token.cont)
    """
    cdup = to_int_or_zero(pop_named_token_and_value(tokens, Tok.cdup))
    
    action = ActionPrint(cdup)

    ix = index_of_token(tokens, Tok.delete)
    if ix is not None:
        tokens.pop(ix)
        action = ActionDelete(cdup)
    
    ix_exec = index_of_token(tokens, Tok.exec)
    ix_semicolon = index_of_token(tokens, Tok.semicolon)

    if ix_exec is not None:
        if ix_semicolon is None:
            raise ValueError("Invalid exec expression: semicolon not found")
        exec_tokens = tokens[ix_exec+1:ix_semicolon]
        action = ActionExec(exec_tokens, cdup)
        tokens = tokens[:ix_exec] + tokens[ix_semicolon+1:]

    paths = []
    pop_paths(tokens, paths, 0)
    pop_paths(tokens, paths, -1)

    """
    i = len(tokens)-1
    while i > -1 and tokens[i].type == Tok.und:
        i -= 1
    tokens, paths1 = tokens[:i+1], tokens[i+1:]
    i = 0
    while i < len(tokens) and tokens[i].type == Tok.und:
        i += 1
    paths2 = []
    if i > 0:
        paths2, tokens = tokens[:i], tokens[i:]
    """

    #expr = tokens
    #paths = [e.cont for e in paths1 + paths2]

    #print('expr, paths', expr, paths)

    extraArgs = ExtraArgs(maxdepth=maxdepth, first=first, last=last)

    return tokens, paths, action, extraArgs

def pop_paths(tokens, paths, index):
    while len(tokens) > 0 and tokens[index].type == Tok.und:
        path = tokens[index].cont
        if has_magic(path):
            paths_ = glob_paths_dirs([path])
            if len(paths_):
                raise ValueError("no such path {}".format(path))
            for p in paths_:
                paths.append(p)
        else:
            if os.path.isdir(path):
                paths.append(path)
            else:
                raise ValueError("no such path {}".format(path))
        tokens.pop(index)

class Cache:

    # todo optimize cache for perfomance and memory (do dictionary lookups become costly for huge dictionaries?)

    def __init__(self):
        self._mtime = dict()
        self._ctime = dict()
        self._size = dict()
        self._parse_size = dict()
        self._now = datetime.datetime.now()
        self._parse_date = dict()

    def mtime(self, path):
        if path not in self._mtime:
            self._mtime[path] = None
            try:
                self._mtime[path] = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            except Exception as e:
                eprint(e)
        return self._mtime[path]

    def ctime(self, path):
        if path not in self._ctime:
            self._ctime[path] = None
            try:
                self._ctime[path] = datetime.datetime.fromtimestamp(os.path.getctime(path))
            except Exception as e:
                eprint(e)
        return self._ctime[path]

    def size(self, path):
        if path not in self._size:
            self._size[path] = None
            try:
                self._size[path] = os.path.getsize(path)
            except Exception as e:
                eprint(e)
        return self._size[path]

    def parse_date(self, date):
        if date not in self._parse_date:
            self._parse_date[date] = None
            try:
                self._parse_date[date] = dateutil.parser.parse(date)
            except Exception as e:
                eprint("Invalid datetime format {}".format(date))
        return self._parse_date[date]

    def parse_size(self, arg):
        if arg not in self._parse_size:
            self._parse_size[arg] = None
            parsed = parse_size(arg)
            if parsed is None:
                eprint("Invalid size format {}".format(arg))
            else:
                self._parse_size[arg] = parsed
        return self._parse_size[arg]

    def now(self):
        return self._now

def pred_mmin(name, path, is_dir, arg, cache):
    mtime = cache.mtime(path)
    if mtime is None:
        return None
    total_min = (cache.now() - mtime).total_seconds() / 60
    arg = float(arg)
    if arg < 0:
        return total_min < abs(arg)
    return total_min > arg

def pred_iname(name, path, is_dir, arg, cache):
    return fnmatch.fnmatch(name, arg)

def pred_ipath(name, path, is_dir, arg, cache):
    return fnmatch.fnmatch(path, arg)

def pred_path(name, path, is_dir, arg, cache):
    return fnmatch.fnmatchcase(path, arg)

def pred_type(name, path, is_dir, arg, cache):
    # todo validate type arg
    return is_dir == (arg == 'd')

def greater(d1, d2):
    if None in [d1, d2]:
        return None
    return d1 > d2

def pred_newer(name, path, is_dir, arg, cache):
    #print([cache.mtime(path), cache.mtime(arg), cache.mtime(path) > cache.mtime(arg), arg])
    return greater(cache.mtime(path), cache.mtime(arg))
    
def pred_newermt(name, path, is_dir, arg, cache):
    return greater(cache.mtime(path), cache.parse_date(arg))

def pred_newerct(name, path, is_dir, arg, cache):
    return greater(cache.ctime(path), cache.parse_date(arg))

def pred_xtime(arg, cache, xtime):
    if xtime is None:
        return None
    total_days = (cache.now() - xtime).total_seconds() / 60 / 60 / 24
    arg = float(arg)
    if arg < 0:
        return total_days < abs(arg)
    return total_days > arg

def pred_mtime(name, path, is_dir, arg, cache):
    return pred_xtime(arg, cache, cache.mtime(path))

def pred_ctime(name, path, is_dir, arg, cache):
    return pred_xtime(arg, cache, cache.ctime(path))

def pred_size(name, path, is_dir, arg, cache):
    if is_dir:
        return None
    size_arg = cache.parse_size(arg)
    size_path = cache.size(path)
    if None in [size_arg, size_path]:
        return None
    if size_arg < 0:
        return size_path < abs(size_arg)
    return size_path > size_arg

def pred_xcont(name, path, is_dir, arg, cache, flags, bin):
    if is_dir:
        return None
    try:
        with open(path, 'rb') as f:
            data = f.read()
        if bin:
            arg = arg.encode("utf-8").decode('unicode_escape').encode("utf-8")
        else:
            arg = arg.encode("utf-8")
        return re.search(arg, data, flags) is not None

    except Exception as e:
        eprint(e)
    return None

def pred_icont(name, path, is_dir, arg, cache):
    return pred_xcont(name, path, is_dir, arg, cache, re.IGNORECASE, False)

def pred_cont(name, path, is_dir, arg, cache):
    return pred_xcont(name, path, is_dir, arg, cache, 0, False)

def pred_bcont(name, path, is_dir, arg, cache):
    return pred_xcont(name, path, is_dir, arg, cache, 0, True)

def max_level(tree):
    level = -1
    for e in tree:
        if isinstance(e, tuple):
            level = max(level, e[1])
    return level

def index_op_par(tree, level):
    for i, e in enumerate(tree):
        if isinstance(e, tuple):
            if isinstance(e[0], NodeOpPar) and e[1] == level:
                return i

def index_cl_par(tree, level, ix_op):
    for i in range(ix_op + 1, len(tree)):
        e = tree[i]
        if isinstance(e, tuple):
            if isinstance(e[0], NodeClPar) and e[1] == level:
                return i

def find_level(tree, level):
    ix_op = index_op_par(tree, level)
    if ix_op is None:
        return None, None
    ix_cl = index_cl_par(tree, level, ix_op)
    if ix_cl is None:
        # unbalanced parenthesis
        return None, None
    return ix_op, ix_cl + 1

def group_tail(tokens):
    i = 0
    if len(tokens) < 1:
        return -1
    if tokens[i][0] == Tok.not_:
        i += 1
    if i > len(tokens):
        return -1
    if tokens[i][0] in tok_pred:
        i += 2
    if i > len(tokens):
        return -1
    if i == 0:
        return -1
    return i

def normalize(nodes):
    res = []
    for node in nodes:
        if isinstance(node, list) and len(node) == 1:
            res.append(node[0])
        else:
            res.append(node)
    return res

class NodeGroupAnd:
    def __init__(self, nodes):
        self._children = normalize(nodes)

    def eval(self, name, path, is_dir, cache):
        for child in self._children:
            res = child.eval(name, path, is_dir, cache)
            if res in [None, False]:
                return res
        # all True
        return True

    def __repr__(self):
        return "NodeGroupAnd({})".format(repr(self._children))

class NodeGroupOr:
    def __init__(self, nodes):
        self._children = normalize(nodes)
    
    def eval(self, name, path, is_dir, cache):
        for child in self._children:
            res = child.eval(name, path, is_dir, cache)
            if res in [None, True]:
                return res
        # all False
        return False

    def __repr__(self):
        return "NodeGroupOr({})".format(repr(self._children))

class NodeGroupNot:
    def __init__(self, children):
        if len(children) != 1:
            raise ValueError("NodeGroupNot unexpected child count {}".format(repr(children)))
        self._child = children[0]

    def eval(self, name, path, is_dir, cache):
        res = self._child.eval(name, path, is_dir, cache)
        if res is None:
            return None
        return not res

    def __repr__(self):
        return "NodeGroupNot({})".format(repr(self._child))

def strip_level(tokens):
    return [e[0] if isinstance(e, tuple) else e for e in tokens]

def pred_token_index(tokens):
    for i, token in enumerate(tokens):
        if not isinstance(token, T):
            continue
        if token.type in tok_pred:
            return i
    return -1

# todo single instance (NodeOr in self._children)

class NodeOpPar:
    def __repr__(self) -> str:
        return '('

class NodeClPar:
    def __repr__(self) -> str:
        return ')'

class NodeNot:
    def __repr__(self) -> str:
        return 'Not'

class NodeAnd:
    def __repr__(self) -> str:
        return 'And'

class NodeOr:
    def __repr__(self) -> str:
        return 'Or'

class NodePred:
    def __init__(self, tokens):
        self._tokens = tokens
        type_, arg = self._type_and_arg()

    def __repr__(self) -> str:
        type_, arg = self._type_and_arg()
        type_str = inv_m[type_]
        if len(self._tokens) == 2:
            return 'NodePred({} {})'.format(type_str, arg)
        else:
            return 'NodePred(-not {} {})'.format(type_str, arg)

    def _type_and_arg(self):
        return self._tokens[-2].type, self._tokens[-1].cont

    def eval(self, name, path, is_dir, cache):

        exp = False if self._tokens[0].type == Tok.not_ else True
        type_, arg = self._type_and_arg()
        
        if arg is None:
            return None

        res = {
            Tok.type: pred_type,
            Tok.mmin: pred_mmin,
            Tok.iname: pred_iname,
            Tok.newer: pred_newer,
            Tok.newermt: pred_newermt,
            Tok.newerct: pred_newerct,
            Tok.ctime: pred_ctime,
            Tok.mtime: pred_mtime,
            Tok.size: pred_size,
            Tok.cont: pred_cont,
            Tok.icont: pred_icont,
            Tok.bcont: pred_bcont,
            Tok.path: pred_path,
            Tok.ipath: pred_ipath,
        }[type_](name, path, is_dir, arg, cache)

        if res is None:
            return None
        return res == exp

def index_of_two(items, pred):
    res = []
    for i, item in enumerate(items):
        res.append(pred(item))
        if res[-2:] == [True, True]:
            return i-1

def indexes_of_two_plus(items, pred):
    b = index_of_two(items, pred)
    if b is None:
        return None, None
    for i in range(b+2, len(items)):
        if not pred(items[i]):
            return b, i
    return b, len(items)

def to_children(nodes):
    #print("to_children({})".format(repr(nodes)))
    if isinstance(nodes[-1], NodeClPar):
        if isinstance(nodes[0], NodeNot):
            return [NodeGroupNot(to_children(nodes[2:-1]))]
        else:
            return to_children(nodes[1:-1])
    else:
        if len(nodes) == 1:
            return nodes

        i = 0
        while True:
            i += 1
            if i > 100:
                t = 1
            b, e = indexes_of_two_plus(nodes, lambda node: not isinstance(node, NodeOr))
            if b is None:
                return [NodeGroupOr(without_or(nodes))]
            nodes = nodes[:b] + [NodeGroupAnd(nodes[b:e])] + nodes[e:]
            if len(nodes) == 1:
                return nodes

def without_or(nodes):
    return [node for node in nodes if not isinstance(node, NodeOr)]

def expr_to_pred(expr):

    level = 0
    
    while True:
        i = pred_token_index(expr)
        if i > -1:
            if i > 0 and isinstance(expr[i-1], T) and expr[i-1].type == Tok.not_:
                head = i-1
            else:
                head = i
            expr = expr[:head] + [NodePred(expr[head: i+2])] + expr[i+2:]
            t = 1
            #print(expr)
        else:
            break

    for i, tok in enumerate(expr):
        if isinstance(tok, T):
            expr[i] = {
                Tok.op_par: NodeOpPar,
                Tok.cl_par: NodeClPar,
                Tok.and_: NodeAnd,
                Tok.or_: NodeOr,
                Tok.not_: NodeNot,
            }[tok.type]()

    expr = [e for e in expr if not isinstance(e, NodeAnd)]

    tree = []

    for i, tok in enumerate(expr):
        
        if isinstance(tok, NodeOpPar):
            level += 1
            tree.append((tok, level))
        elif isinstance(tok, NodeClPar):
            tree.append((tok, level))
            level -= 1
        else:
            tree.append((tok, level))

    if len(tree) == 0:
        return tree, lambda name, path, is_dir: True
    
    while (True):
        level = max_level(tree)
        if level < 0:
            children = strip_level(tree)
            tree = to_children(children)
            break
        h, t = find_level(tree, level)

        if h is None:
            children = strip_level(tree)
            tree = to_children(children)
            break
        else:
            if h > 0 and isinstance(tree[h-1][0], NodeNot):
                h = h-1
            children = strip_level(tree[h:t])
            tree = tree[:h] + [to_children(children)] + tree[t:]

    if len(tree) != 1:
        raise ValueError("Unexpected tree size {}".format(repr(tree)))
    
    tree = tree[0]

    #print(tree)

    cache = Cache()

    return tree, lambda name, path, is_dir: tree.eval(name, path, is_dir, cache)

def walk(top, topdown=True, onerror=None, followlinks=False, maxdepth=0):
    return _walk(os.fspath(top), topdown, onerror, followlinks, maxdepth)

def _walk(top, topdown, onerror, followlinks, maxdepth):
    dirs = []
    nondirs = []
    walk_dirs = []
    try:
        scandir_it = os.scandir(top)
    except OSError as error:
        if onerror is not None:
            onerror(error)
        return

    with scandir_it:
        while True:
            try:
                try:
                    entry = next(scandir_it)
                except StopIteration:
                    break
            except OSError as error:
                if onerror is not None:
                    onerror(error)
                return

            try:
                is_dir = entry.is_dir()
            except OSError:
                is_dir = False

            if is_dir:
                dirs.append(entry.name)
            else:
                nondirs.append(entry.name)

            if not topdown and is_dir:
                if followlinks:
                    walk_into = True
                else:
                    try:
                        is_symlink = entry.is_symlink()
                    except OSError:
                        is_symlink = False
                    walk_into = not is_symlink

                if walk_into:
                    walk_dirs.append(entry.path)

    maxdepth -= 1
    if maxdepth == 0:
        walk_dirs = []

    if topdown:
        yield top, dirs, nondirs
        if maxdepth == 0:
            return
        islink, join = os.path.islink, os.path.join
        for dirname in dirs:
            new_path = join(top, dirname)
            if followlinks or not islink(new_path):
                yield from _walk(new_path, topdown, onerror, followlinks, maxdepth)
    else:
        for new_path in walk_dirs:
            yield from _walk(new_path, topdown, onerror, followlinks, maxdepth)
        yield top, dirs, nondirs

def print_help():
    print("""usage: pyfind [conditions] [-exec cmd args {} ;] [-delete]

finds files and dirs that satisfy conditions (predicates)

predicates:
  -mtime DAYS          if DAYS is negative: modified within DAYS days, 
                       if positive modified more than DAYS days ago
  -ctime DAYS          same as -mtime, but when modified metadata not content
  -mmin MINUTES        if MINUTES is negative: modified within MINUTES minutes, 
                       if positive modified more than MINUTES minutes ago
  -cmin MINUTES        same as -mmin, but when modified metadata not content
  -newer PATH/TO/FILE  modified later than PATH/TO/FILE
  -newermt DATETIME    modified later than DATETIME
  -newerct DATETIME    same as -newermt but when modified metadata not content
  -name PATTERN        filename matches PATTERN (wildcard)
  -iname PATTERN       same as -name but case insensitive
  -path PATTERN        file path matches PATTERN
  -ipath PATTERN       same as -path but case insensitive
  -cont PATTERN        file contains PATTERN
  -icont PATTERN       same as -cont but case insensitive
  -bcont PATTERN       same as -cont but PATTERN is binary expression
  -type d              is directory
  -type f              is file
  -cdup N              print (or take action) parent path (strip N trailing components from path)
  -first N             print (or take action) on first N found items
  -last N              print (or take action) on last N found items

predicates can be inverted using -not, can be grouped together in boolean expressions 
using -or and -and and parenthesis

examples:
  pyfind -iname *.py -mmin -10
  pyfind -iname *.cpp -or -iname *.h -not ( -iname moc_* -or -iname ui_* )
  pyfind -iname *.h -exec pygrep -H class {} ;
  pyfind -iname *.o -delete
  pyfind -iname *.py | pyxargs pywc -l
  pyfind D:\\dev -iname .git -type d -cdup 1
""")

def main():

    args = sys.argv[1:]
    if '-h' in args or '--help' in args:
        print_help()
        return

    expr, paths, action, extraArgs = parse_args()
    tree, pred = expr_to_pred(expr)
    if len(paths) == 0:
        paths.append(".")

    collect = extraArgs.last is not None

    collected = []

    executed = 0

    for path in paths:
        for root, dirs, files in walk(path, maxdepth=extraArgs.maxdepth):
            for name in dirs:
                p = os.path.join(root, name)
                if pred(name, p, True):
                    action.exec(path, name, p, True)
            for name in files:
                p = os.path.join(root, name)
                if pred(name, p, False):
                    if collect:
                        collected.append((path, name, p, False))
                    else:
                        action.exec(path, name, p, False)
                        executed += 1
                        if extraArgs.first == executed:
                            return 
    if collect:
        for item in collected[-extraArgs.last:]:
            action.exec(*item)

def unquote(s):
    if s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s

if __name__ == "__main__":
    main()