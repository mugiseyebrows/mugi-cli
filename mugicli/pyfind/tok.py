from typing import Any
from dataclasses import dataclass

class TOK:
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
        flush,
        touch,
        cpptmp,
        docgrep,
        xlgrep,
        gitstat,
        gitdir,
    ) = range(48)
    
def tok_type_as_string(type):
    for k, v in TOK.__dict__.items():
        if isinstance(v, int):
            if v == type:
                return k

TOK_AS_INT = {
    "(": TOK.op_par,
    ")": TOK.cl_par,
    "!": TOK.not_,
    "-not": TOK.not_,
    "-a": TOK.and_,
    "-and": TOK.and_,
    "-o": TOK.or_,
    "-or": TOK.or_,
    "-mmin": TOK.mmin,
    "-iname": TOK.iname,
    "-name": TOK.name,
    "-type": TOK.type,
    "f": TOK.f,
    "d": TOK.d,
    "-newer": TOK.newer,
    "-newermt": TOK.newermt,
    "-newerct": TOK.newerct,
    "-mtime": TOK.mtime,
    "-ctime": TOK.ctime,
    "-size": TOK.size,
    "-exec": TOK.exec,
    "-async": TOK.async_,
    "-delete": TOK.delete,
    ";": TOK.semicolon,
    "\\;": TOK.semicolon,
    "{}": TOK.pathbind,
    "{path}": TOK.pathbind,
    "{name}": TOK.namebind,
    "{nameext}": TOK.nameextbind,
    "-grep": TOK.grep,
    "-igrep": TOK.igrep,
    "-bgrep": TOK.bgrep,
    "-path": TOK.path,
    "-ipath": TOK.ipath,
    "-maxdepth": TOK.maxdepth,
    "-cdup": TOK.cdup,
    "-first": TOK.first,
    "-abspath": TOK.abspath,
    "-conc": TOK.conc,
    "-trail": TOK.trail,
    "-xargs": TOK.xargs,
    "-mdate": TOK.mdate,
    "-stat": TOK.stat,
    "-print": TOK.print,
    "-touch": TOK.touch,
    "-flush": TOK.flush,
    "-cpptmp": TOK.cpptmp,
    "-docgrep": TOK.docgrep,
    "-xlgrep": TOK.xlgrep,
    "-gitstat": TOK.gitstat,
    "-gitdir": TOK.gitdir,
}

TOK_AS_STR = {v:k for k,v in TOK_AS_INT.items()}

@dataclass
class T:
    type: int
    cont: str
    val: Any = None

tok_pred_noargs = [TOK.gitdir, TOK.cpptmp]

tok_pred_nargs = [TOK.name, TOK.iname, TOK.path, TOK.ipath, TOK.mdate, TOK.xlgrep]

tok_pred = [TOK.mmin, TOK.name, TOK.iname, TOK.type, TOK.newer, 
    TOK.newerct, TOK.newermt, TOK.mtime, TOK.ctime, TOK.size, TOK.grep, 
    TOK.igrep, TOK.bgrep, TOK.path, TOK.ipath, TOK.mdate, TOK.docgrep, TOK.xlgrep, 
    TOK.gitdir, TOK.cpptmp]