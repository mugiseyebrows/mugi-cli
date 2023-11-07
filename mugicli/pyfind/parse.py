import sys
import os
from dataclasses import dataclass

from .tok import T, TOK, TOK_AS_INT, tok_pred, tok_pred_nargs
from . import predicate
from .action import ActionPrint, ActionExec, ActionDelete
from ..shared import has_magic, glob_paths_dirs
from .. import parse_size
import dateutil.parser
import datetime

@dataclass
class ExtraArgs:
    maxdepth: int
    first: int

def last_und_index(tokens, i):
    index = None
    for i in range(i, len(tokens)):
        if tokens[i].type == TOK.und and not tokens[i].cont.startswith("-"):
            index = i
        else:
            return index
    return index

def index_of_token(tokens, type):
    for i, tok in enumerate(tokens):
        if tok.type == type:
            return i

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
    
def pop_paths(tokens, paths, index):
    while len(tokens) > 0 and tokens[index].type == TOK.und:
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

def parse_args(args = None):
    if args is None:
        args = sys.argv[1:]
    tokens = [T(TOK_AS_INT[t], t) if t in TOK_AS_INT else T(TOK.und, t) for t in args]
    for i, tok in enumerate(tokens):
        if tok is None:
            continue

        if tok.type in tok_pred_nargs:
            index = last_und_index(tokens, i+1)
            cont = [t.cont for t in tokens[i+1:index+1]]
            tokens[index] = T(TOK.arg, cont=cont)
            for j in range(i+1, index):
                tokens[j] = None

        elif tok.type in tok_pred:
            token = tokens[i+1]
            tokens[i+1] = T(TOK.arg, token.cont)

    tokens = [t for t in tokens if t is not None]

    ix_exec = index_of_token(tokens, TOK.exec)
    ix_slashsemicolon = index_of_token(tokens, TOK.slashsemicolon)

    exec_tokens = None
    if ix_exec is not None:
        if ix_slashsemicolon is None:
            raise ValueError("Invalid exec expression: semicolon not found")
        ix_tail = ix_slashsemicolon
        if ix_tail < ix_exec:
            raise ValueError("\; preceedes -exec")
        exec_tokens = tokens[ix_exec+1:ix_tail]
        tokens = tokens[:ix_exec] + tokens[ix_tail+1:]

    print_ = pop_named_token(tokens, TOK.print)

    stat = pop_named_token(tokens, TOK.stat)

    trail = pop_named_token(tokens, TOK.trail)

    conc = pop_named_token_and_value(tokens, TOK.conc, type=int)

    async_ = pop_named_token(tokens, TOK.async_)

    xargs = pop_named_token(tokens, TOK.xargs)

    action = ActionPrint(stat, trail)

    if exec_tokens:
        action = ActionExec(exec_tokens, async_, conc, xargs)
    
    maxdepth = pop_named_token_and_value(tokens, TOK.maxdepth, type=int)
    if maxdepth is None:
        maxdepth = 0
    
    first = pop_named_token_and_value(tokens, TOK.first, type=int)

    delete = pop_named_token(tokens, TOK.delete)
    if delete:
        action = ActionDelete()

    cdup = pop_named_token_and_value(tokens, TOK.cdup, type=int)
    if cdup is None:
        cdup = 0

    abspath = pop_named_token(tokens, TOK.abspath)

    action.setOptions(cdup, abspath)

    paths = []
    pop_paths(tokens, paths, 0)
    pop_paths(tokens, paths, -1)

    unrecognized = []
    for t in tokens:
        if t.type == TOK.und:
            unrecognized.append(t)
    if len(unrecognized) > 0:
        print(tokens)
        raise ValueError("unrecognized tokens {}".format([t.cont for t in unrecognized]))

    extraArgs = ExtraArgs(maxdepth=maxdepth, first=first)

    for i, tok in enumerate(tokens):
        if tok.type == TOK.size:
            tokens[i+1].val = parse_size(tokens[i+1].cont)
        elif tok.type == TOK.type:
            arg = tokens[i+1].cont
            if arg not in ['d','f']:
                raise ValueError("{} is not a valid type".format(arg))
            tokens[i+1].val = arg
        elif tok.type in [TOK.newermt, TOK.newerct]:
            arg = tokens[i+1].cont
            tokens[i+1].val = dateutil.parser.parse(arg)
        elif tok.type in [TOK.mtime, TOK.ctime, TOK.mmin]:
            arg = tokens[i+1].cont
            tokens[i+1].val = float(arg)
        elif tok.type == TOK.mdate:
            arg = tokens[i+1].cont
            tokens[i+1].val = [datetime.datetime.strptime(s, "%Y-%m-%d") for s in arg]
        elif tok.type == TOK.newer:
            arg = tokens[i+1].cont
            tokens[i+1].val = predicate._getmtime(arg)

    return tokens, paths, action, extraArgs
