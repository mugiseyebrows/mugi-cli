import sys
import os
from dataclasses import dataclass

from .tok import T, TOK, TOK_AS_INT, tok_pred, tok_pred_nargs, tok_pred_noargs
from . import predicate
from .action import ActionPrint, ActionExec, ActionDelete, ActionTouch, ActionGitStatus
from ..shared import has_magic, glob_paths_dirs
from .. import parse_size
import dateutil.parser
import re
from .types import parse_address_range, parse_int, parse_float, parse_float_range, ExtraArgs, Pred

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

def pop_named_token(tokens, t) -> bool:
    ix = index_of_token(tokens, t)
    if ix is None:
        return False
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
    tokens: list[T] = [T(TOK_AS_INT[t], t) if t in TOK_AS_INT else T(TOK.und, t) for t in args]
    for i, tok in enumerate(tokens):
        if tok is None:
            continue

        if tok.type in tok_pred_nargs:
            #index = last_und_index(tokens, i+1)
            #cont = [t.cont for t in tokens[i+1:index+1]]
            #tokens[index] = T(TOK.arg, cont=cont)
            #for j in range(i+1, index):
            #    tokens[j] = None
            for j in range(i+1, len(tokens)):
                if tokens[j].cont.startswith('-'):
                    break
                tokens[j] = T(TOK.arg, tokens[j].cont)
        elif tok.type in tok_pred_noargs:
            pass
        elif tok.type in tok_pred:
            token = tokens[i+1]
            tokens[i+1] = T(TOK.arg, token.cont)

    tokens = [t for t in tokens if t is not None]

    ix_exec = index_of_token(tokens, TOK.exec)
    ix_semicolon = index_of_token(tokens, TOK.semicolon)

    exec_tokens = None
    if ix_exec is not None:
        if ix_semicolon is None:
            raise ValueError("Invalid exec expression: semicolon not found")
        ix_tail = ix_semicolon
        if ix_tail < ix_exec:
            raise ValueError("\\; preceedes -exec")
        exec_tokens = tokens[ix_exec+1:ix_tail]
        tokens = tokens[:ix_exec] + tokens[ix_tail+1:]

    print_ = pop_named_token(tokens, TOK.print)

    stat = pop_named_token(tokens, TOK.stat)

    trail = pop_named_token(tokens, TOK.trail)

    conc = pop_named_token_and_value(tokens, TOK.conc, type=int)

    async_ = pop_named_token(tokens, TOK.async_)

    xargs = pop_named_token(tokens, TOK.xargs)

    flush = pop_named_token(tokens, TOK.flush)

    action = ActionPrint(stat, trail, flush)

    if exec_tokens:
        action = ActionExec(exec_tokens, async_, conc, xargs)
    
    maxdepth = pop_named_token_and_value(tokens, TOK.maxdepth, type=int)
    if maxdepth is None:
        maxdepth = 0
    
    first = pop_named_token_and_value(tokens, TOK.first, type=int)

    delete = pop_named_token(tokens, TOK.delete)
    if delete:
        action = ActionDelete()

    touch = pop_named_token(tokens, TOK.touch)
    if touch:
        action = ActionTouch()

    gitstat = pop_named_token(tokens, TOK.gitstat)
    if gitstat:
        action = ActionGitStatus()

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
            """
            if i+2 < len(tokens) and tokens[i+2].type == TOK.arg:
                nargs = 2
            else:
                nargs = 1
            """
            nargs = get_nargs(tokens, i)
            for j in range(i+1, i+1+nargs):
                tokens[j].val = dateutil.parser.parse(tokens[j].cont).date()
        elif tok.type == TOK.newer:
            arg = tokens[i+1].cont
            tokens[i+1].val = predicate._getmtime(arg)
        elif tok.type == TOK.xlgrep:
            nargs = get_nargs(tokens, i)
            for j in range(i + 1, i + 1 + nargs):
                tokens[j].val = parse_xlgrep_arg(tokens[j].cont)
        elif tok.type == TOK.bgrep:
            tokens[i+1].val = parse_bgrep_arg(tokens[i+1].cont)
            
    return tokens, paths, action, extraArgs

def hex_parse(s):
    res = []
    for i in range(0, len(s), 2):
        res.append(int(s[i:i+2], 16))
    return bytes(res)

def parse_bgrep_arg(arg: str):
    return hex_parse(re.sub('\\s+','', arg))

def parse_xlgrep_arg(s):
    ar = parse_address_range(s)
    if ar:
        return ar
    i = parse_int(s)
    if i is not None:
        return i
    f = parse_float(s)
    if f is not None:
        return f
    fr = parse_float_range(s)
    if fr:
        return fr
    return s

def get_nargs(tokens: list[T], i):
    count = 0
    for j in range(i+1, len(tokens)):
        if tokens[j].cont.startswith('-'):
            return count
        count += 1
    return count