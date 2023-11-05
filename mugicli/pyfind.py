import os
import datetime
import sys
import re
from .shared import eprint, glob_paths_dirs, has_magic, run, adjust_command, split_list, debug_print
import sys
from dataclasses import dataclass
from itertools import count
import subprocess
import shutil
import fnmatch
from . import parse_size, print_utf8, walk
from typing import Any
from bashrange import expand_args
import asyncio
from functools import reduce, lru_cache
import time
import tempfile

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
        conc,
        delete,
        semicolon,
        slashsemicolon,
        pathbind,
        grep,
        igrep,
        bgrep,
        maxdepth,
        cdup,
        first,
        abspath,
        namebind,
        nameextbind,
        trail,
        xargs,
        mdate,
        stat,
        async_,
        print,
    ) = range(42)
    
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
    "-async": Tok.async_,
    "-delete": Tok.delete,
    ";": Tok.semicolon,
    "{}": Tok.pathbind,
    "{path}": Tok.pathbind,
    "{name}": Tok.namebind,
    "{nameext}": Tok.nameextbind,
    "-grep": Tok.grep,
    "-igrep": Tok.igrep,
    "-bgrep": Tok.bgrep,
    "-path": Tok.path,
    "-ipath": Tok.ipath,
    "-maxdepth": Tok.maxdepth,
    "-cdup": Tok.cdup,
    "-first": Tok.first,
    "-abspath": Tok.abspath,
    "-conc": Tok.conc,
    "-trail": Tok.trail,
    "-xargs": Tok.xargs,
    "-mdate": Tok.mdate,
    "-stat": Tok.stat,
    "-print": Tok.print,
    "\\;": Tok.slashsemicolon
}

inv_m = {v:k for k,v in m.items()}

@dataclass
class T:
    type: int
    cont: Any

tok_pred_nargs = [Tok.name, Tok.iname, Tok.path, Tok.ipath, Tok.mdate]

tok_pred = [Tok.mmin, Tok.name, Tok.iname, Tok.type, Tok.newer, 
    Tok.newerct, Tok.newermt, Tok.mtime, Tok.ctime, Tok.size, Tok.grep, Tok.igrep, Tok.bgrep, Tok.path, Tok.ipath, Tok.mdate]

def cdup_path(path, cdup):
    for i in range(cdup):
        if '/' in path or '\\' in path:
            path = os.path.dirname(path)
        else:
            path = os.path.dirname(os.path.realpath(path))
    return path


class ActionBase:

    def __init__(self):
        self._cdup = None
        self._abspath = None
        self._queue = None
        self._count = 0

    def setOptions(self, cdup, abspath):
        self._cdup = cdup
        self._abspath = abspath

    async def wait(self):
        pass

# =================== <Executor>

class ExecutorLogger:
    def __init__(self):
        self._data = []

    def log(self, cmd, stdout_name, stderr_name, returncode):
        self._data.append((cmd, stdout_name, stderr_name, returncode))
        #print("stdout_name, stderr_name", stdout_name, stderr_name)

    def flush(self):
        stdout_fd, stdout_name = tempfile.mkstemp(prefix='pyfind-exec-complete-', suffix='.stdout')
        stderr_fd, stderr_name = tempfile.mkstemp(prefix='pyfind-exec-complete-', suffix='.stderr')

        def write(fd, cmd_, data):
            os.write(fd, cmd_)
            os.write(fd, data)
            os.write(fd, b"\n")

        for item in self._data:
            cmd, input_stdout_name, input_stderr_name, returncode = item
            cmd_ = (" ".join(cmd) + "\n").encode('utf-8')
            with open(input_stdout_name, 'rb') as f:
                write(stdout_fd, cmd_, f.read())
            with open(input_stderr_name, 'rb') as f:
                write(stderr_fd, cmd_, f.read())
        os.close(stdout_fd)
        os.close(stderr_fd)

        eprint("stdout data saved to {}".format(stdout_name))
        eprint("stderr data saved to {}".format(stderr_name))

class Executor:
    def exec(self, cmd):
        pass
    async def wait(self):
        pass

class SyncExecutor(Executor):
    def exec(self, cmd):
        cmd_ = adjust_command(cmd)
        subprocess.run(cmd_)

    async def wait(self):
        pass

class XargsExecutor(Executor):
    def __init__(self, cmd):
        super().__init__()
        self._paths = []
        self._cmd = cmd
    
    def append(self, path):
        self._paths.append(path)

    async def wait(self):
        cmd_ = adjust_command(self._cmd + self._paths)
        subprocess.run(cmd_)

async def executor_worker(name, queue, logger: ExecutorLogger):
    t0 = time.time()
    while True:
        debug_print(name, "waiting for new task")
        cmd = await queue.get()
        t1 = time.time()
        debug_print(name, "got task")
        
        stdout_fd, stdout_name = tempfile.mkstemp(prefix='pyfind-exec-', suffix='.stdout')
        stderr_fd, stderr_name = tempfile.mkstemp(prefix='pyfind-exec-', suffix='.stderr')

        cmd_ = adjust_command(cmd)

        debug_print(name, "running", cmd)
        proc = await asyncio.subprocess.create_subprocess_exec(*cmd_, stdout=stdout_fd, stderr=stderr_fd)
        
        debug_print(name, "wait process to complete")
        await proc.wait()

        os.close(stdout_fd)
        os.close(stderr_fd)

        logger.log(cmd, stdout_name, stderr_name, proc.returncode)

        t2 = time.time()

        debug_print(name, "process completed, returncode", proc.returncode, "time", (t1 - t0), (t2 - t0))
        queue.task_done()

class AsyncExecutor(Executor):

    def __init__(self, n = None):
        super().__init__()
        queue = asyncio.Queue()
        if n is None:
            n = os.cpu_count()
        debug_print("create {} workers".format(n))
        workers = []
        logger = ExecutorLogger()
        for i in range(n):
            task = asyncio.create_task(executor_worker("worker {}".format(i), queue, logger))
            workers.append(task)
        self._queue = queue
        self._workers = workers
        self._n = n
        self._logger = logger
    
    def exec(self, cmd):
        self._queue.put_nowait(cmd)

    async def wait(self):
        queue = self._queue

        debug_print("join queue")
        await queue.join()
        debug_print("queue joined")

        debug_print("terminating workers")
        workers = self._workers
        for task in workers:
            task.cancel()
        asyncio.gather(*workers, return_exceptions=True)
        debug_print("workers terminated")

        self._logger.flush()


# =================== </Executor>

def exec_insert_args(tokens, path):
    def to_list(vs):
            if isinstance(vs, list):
                return vs
            return [vs]
    
    def replace_many(s, repls):
        return reduce(lambda acc, e: acc.replace(*e), repls, s)
    cmd = []

    name = os.path.basename(path)
    basename, ext = os.path.splitext(name)
    dirname = os.path.dirname(path)
    for t in tokens:
        for e in to_list(t.cont):
            e = replace_many(e, [
                ("{dirname}", dirname), 
                ("{basename}", basename),
                ("{ext}", ext),
                ("{name}", name),
                ("{path}", path),
                ("{}", path)
            ])
            cmd.append(e)
    return cmd

class ActionExec(ActionBase):
    def __init__(self, tokens, async_, conc, xargs):
        super().__init__()
        self._tokens = tokens
        self._paths = []

        if xargs:
            cmd = exec_insert_args(tokens, "xargs/arg/path")
            executor = XargsExecutor(cmd)
        else:
            if async_ or conc:
                executor = AsyncExecutor(conc)
            else:
                executor = SyncExecutor()
        self._executor = executor

    def exec(self, root, name, path, is_dir):

        path = cdup_path(path, self._cdup)

        if self._abspath:
            path = os.path.realpath(path)

        cmd = exec_insert_args(self._tokens, path)

        executor = self._executor

        if isinstance(executor, XargsExecutor):
            executor.append(path)
        else:
            executor.exec(cmd)

    async def wait(self):
        await self._executor.wait()

class ActionDelete(ActionBase):

    def exec(self, root, name, path, is_dir):
        path = cdup_path(path, self._cdup)
        if is_dir:
            eprint("Removing directory {}".format(path))
            shutil.rmtree(path)
        else:
            eprint("Removing file {}".format(path))
            os.remove(path)

class Printer:
    def __init__(self, stat, trail):
        self._stat = stat
        self._f = None
        self._header = False
        self._trail = trail
    
    def print(self, path):
        path_ = path + ("\\" if self._trail and os.path.isdir(path) else "")
        if self._stat:
            mdate = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            size = os.path.getsize(path)
            text = "{} {:>16} {}".format(
                mdate.strftime("%Y-%m-%d %H:%M:%S"),
                size,
                path_
            )
        else:
            text = path_

        if self._stat and not self._header:
            text = "{:>19} {:>16} {}\n".format("mtime","size","path") + text
            self._header = True

        try:
            print_utf8(text)
        except UnicodeEncodeError as e:
            print(e)

class ActionPrint(ActionBase):

    def __init__(self, stat, trail):
        super().__init__()
        self._printer = Printer(stat, trail)

    def exec(self, root, name, path, is_dir):
        path = cdup_path(path, self._cdup)

        if self._abspath:
            path_ = os.path.realpath(path)
        elif os.path.isabs(root):
            path_ = path
        else:
            path_ = os.path.relpath(path, os.getcwd())

        self._printer.print(path_)

def index_of_token(tokens, type):
    for i, tok in enumerate(tokens):
        if tok.type == type:
            return i

@dataclass
class ExtraArgs:
    maxdepth: int
    first: int

def pop_named_token(tokens, t):
    ix = index_of_token(tokens, t)
    if ix is None:
        return False
    if ix is not None:
        tokens.pop(ix)
        return True

def pop_named_token_and_value(tokens, t, defval = None, type = None):
    ix = index_of_token(tokens, t)
    if ix is None:
        return defval
    if ix is not None:
        token_key = tokens.pop(ix)
        token_value = tokens.pop(ix)
        if type is not None:
            return type(token_value.cont)
        return token_value.cont

def to_int(v):
    if v is None:
        return v
    return int(v)

def to_int_or_zero(v):
    if v is None:
        return 0
    return int(v)

def last_und_index(tokens, i):
    index = None
    for i in range(i, len(tokens)):
        if tokens[i].type == Tok.und and not tokens[i].cont.startswith("-"):
            index = i
        else:
            return index
    return index

def first_truthy(*args):
        for arg in args:
            if arg:
                return arg

def parse_args(args = None):
    if args is None:
        args = sys.argv[1:]
    tokens = [T(m[t], t) if t in m else T(Tok.und, t) for t in args]
    for i, tok in enumerate(tokens):
        if tok is None:
            continue

        if tok.type in tok_pred_nargs:
            index = last_und_index(tokens, i+1)
            cont = [t.cont for t in tokens[i+1:index+1]]
            tokens[index] = T(Tok.arg, cont=cont)
            for j in range(i+1, index):
                tokens[j] = None

        elif tok.type in tok_pred:
            token = tokens[i+1]
            tokens[i+1] = T(Tok.arg, token.cont)

    tokens = [t for t in tokens if t is not None]

    ix_exec = index_of_token(tokens, Tok.exec)
    ix_slashsemicolon = index_of_token(tokens, Tok.slashsemicolon)

    exec_tokens = None
    if ix_exec is not None:
        if ix_slashsemicolon is None:
            raise ValueError("Invalid exec expression: semicolon not found")
        ix_tail = ix_slashsemicolon
        if ix_tail < ix_exec:
            raise ValueError("\; preceedes -exec")
        exec_tokens = tokens[ix_exec+1:ix_tail]
        tokens = tokens[:ix_exec] + tokens[ix_tail+1:]

    print_ = pop_named_token(tokens, Tok.print)

    stat = pop_named_token(tokens, Tok.stat)

    trail = pop_named_token(tokens, Tok.trail)

    conc = pop_named_token_and_value(tokens, Tok.conc, type=int)

    async_ = pop_named_token(tokens, Tok.async_)

    xargs = pop_named_token(tokens, Tok.xargs)

    action = ActionPrint(stat, trail)

    if exec_tokens:
        action = ActionExec(exec_tokens, async_, conc, xargs)
    
    maxdepth = pop_named_token_and_value(tokens, Tok.maxdepth, type=int)
    if maxdepth is None:
        maxdepth = 0
    
    first = pop_named_token_and_value(tokens, Tok.first, type=int)

    delete = pop_named_token(tokens, Tok.delete)
    if delete:
        action = ActionDelete()

    cdup = pop_named_token_and_value(tokens, Tok.cdup, type=int)
    if cdup is None:
        cdup = 0

    abspath = pop_named_token(tokens, Tok.abspath)

    action.setOptions(cdup, abspath)

    paths = []
    pop_paths(tokens, paths, 0)
    pop_paths(tokens, paths, -1)

    unrecognized = []
    for t in tokens:
        if t.type == Tok.und:
            unrecognized.append(t)
    if len(unrecognized) > 0:
        print(tokens)
        raise ValueError("unrecognized tokens {}".format([t.cont for t in unrecognized]))

    extraArgs = ExtraArgs(maxdepth=maxdepth, first=first)

    return tokens, paths, action, extraArgs

def pop_paths(tokens, paths, index):
    while len(tokens) > 0 and tokens[index].type == Tok.und:
        path = tokens[index].cont
        if path.startswith("-"):
            return
        if has_magic(path):
            paths_ = glob_paths_dirs([path])
            if len(paths_) == 0:
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
    for pat in arg:
        if fnmatch.fnmatch(name, pat):
            return True
    return False

def pred_name(name, path, is_dir, arg, cache):
    for pat in arg:
        if fnmatch.fnmatchcase(name, pat):
            return True
    return False

def pred_ipath(name, path, is_dir, arg, cache):
    for pat in arg:
        if fnmatch.fnmatch(path, pat):
            return True
    return False

def pred_path(name, path, is_dir, arg, cache):
    for pat in arg:
        if fnmatch.fnmatchcase(path, pat):
            return True
    return False


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

@lru_cache
def path_mdate(path):
    d = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.datetime(d.year, d.month, d.day)

def pred_mdate(name, path, is_dir, arg, cache):
    d = path_mdate(path)
    ds = [datetime.datetime.strptime(s, "%Y-%m-%d") for s in arg]
    if len(ds) == 1:
        return ds[0] <= d <= ds[0]
    return ds[0] <= d <= ds[1]
    
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

def pred_xgrep(name, path, is_dir, arg, cache, flags, bin):
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

def pred_grep(name, path, is_dir, arg, cache):
    return pred_xgrep(name, path, is_dir, arg, cache, 0, False)

def pred_igrep(name, path, is_dir, arg, cache):
    return pred_xgrep(name, path, is_dir, arg, cache, re.IGNORECASE, False)

def pred_bgrep(name, path, is_dir, arg, cache):
    return pred_xgrep(name, path, is_dir, arg, cache, 0, True)

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
            Tok.name: pred_name,
            Tok.newer: pred_newer,
            Tok.newermt: pred_newermt,
            Tok.newerct: pred_newerct,
            Tok.ctime: pred_ctime,
            Tok.mtime: pred_mtime,
            Tok.size: pred_size,
            Tok.grep: pred_grep,
            Tok.igrep: pred_igrep,
            Tok.bgrep: pred_bgrep,
            Tok.path: pred_path,
            Tok.ipath: pred_ipath,
            Tok.mdate: pred_mdate,
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

def print_help():
    print("""usage: pyfind [PATHS] [OPTIONS] [CONDITIONS] [-async] [-exec cmd args \\{} \;] [-delete] [-print]

finds files and dirs that satisfy conditions (predicates) and executes action

options:
  -maxdepth NUMBER     walk no deeper than NUMBER levels
  -output PATH         output to file instead of stdout
  -append              append to file instead of rewrite
  -abspath             print absolute paths
  -async               execute asyncronously (do not wait for termination)
  -conc NUMBER         concurrency limit for -async -exec, 
                       defaults to number of cpu cores
  -trail               print trailing slash on directories
  -cdup NUMBER         print (or perform action on) parent path (strip NUMBER 
                       trailing components from path)
  -first NUMBER        print (or perform action on) first NUMBER found items and stop
  -xargs               execute command once with all matched files as arguments

actions:
  -delete              delete matched file
  -exec                execute command(s)
  -print               print matched paths to output (default action)
  -stat                print matched paths with file size and modification date

predicates:
  -mtime DAYS          if DAYS is negative: modified within DAYS days, 
                       if positive modified more than DAYS days ago
  -ctime DAYS          same as -mtime, but when modified metadata not content
  -mmin MINUTES        if MINUTES is negative: modified within MINUTES minutes, 
                       if positive modified more than MINUTES minutes ago
  -mdate DATE1 [DATE2] modified at DATE1 (or between DATE1 and DATE2)
  -cmin MINUTES        same as -mmin, but when modified metadata not content
  -newer PATH/TO/FILE  modified later than PATH/TO/FILE
  -newermt DATETIME    modified later than DATETIME
  -newerct DATETIME    same as -newermt but when modified metadata not content
  -name PATTERN        filename matches PATTERN (wildcard)
  -iname PATTERN       same as -name but case insensitive
  -path PATTERN        file path matches PATTERN
  -ipath PATTERN       same as -path but case insensitive
  -grep PATTERN        file content contains PATTERN
  -igrep PATTERN       same as -grep but case insensitive
  -bgrep PATTERN       same as -grep but PATTERN is binary expression
  -type d              is directory
  -type f              is file

predicates can be inverted using -not, can be grouped together in boolean expressions 
using -or and -and and parenthesis

binds:
  {}          path to file
  {path}      path to file
  {name}      name with extension
  {ext}       extension
  {basename}  name without extension
  {dirname}   directory name

examples:
  pyfind -iname *.py -mmin -10
  pyfind -iname *.cpp *.h -not ( -iname moc_* ui_* )
  pyfind -iname *.h -exec pygrep -H class {} \;
  pyfind -iname *.o -delete
  pyfind -iname *.py -xargs -exec wc -l \;
  pyfind D:\\dev -iname .git -type d -cdup 1
  pyfind -iname *.dll -cdup 1 -abspath | pysetpath -o env.bat
  pyfind -iname *.mp3 -conc 4 -async -exec ffmpeg -i {} {dirname}\\{basename}.wav \;
  pyfind -mdate 2023-11-05
""")

async def async_main():

    args = expand_args()
    
    if len(args) > 0 and args[-1] in ['-h', '--help']:
        print_help()
        return

    expr, paths, action, extraArgs = parse_args(args)
    tree, pred = expr_to_pred(expr)

    if len(paths) == 0:
        paths.append(".")

    executed = 0

    def need_to_stop():
        nonlocal executed
        return extraArgs.first is not None and executed >= extraArgs.first

    def walk_all():
        nonlocal executed
        for path in paths:
            for root, dirs, files in walk(path, maxdepth=extraArgs.maxdepth):
                for name in dirs:
                    p = os.path.join(root, name)
                    if pred(name, p, True):
                        action.exec(path, name, p, True)
                        executed += 1
                        if need_to_stop():
                            return
                for name in files:
                    p = os.path.join(root, name)
                    if pred(name, p, False):
                        action.exec(path, name, p, False)
                        executed += 1
                        if need_to_stop():
                            return
    
    walk_all()

    await action.wait()

def unquote(s):
    if s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()