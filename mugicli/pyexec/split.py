import re

def unquote(s):
    if len(s) > 1 and s[0] == "'" and s[-1] == "'":
        return s[1:-1]
    return s

def single_quote_split(args):
    res = []
    for s in args:
        pos = [0]
        ins = False
        for i,c in enumerate(s):
            if c == "'":
                if ins:
                    pos.append(i+1)
                else:
                    pos.append(i)
                ins = not ins
        pos.append(len(s))
        #print(pos)
        
        for h,t in zip(pos, pos[1:]):
            res.append(s[h:t])
    #print("single_quote_split", args)
    return res

def space_split(args):
    res = []
    for e in args:
        if len(e) > 0 and e[0] == "'":
            res.append(e)
        else:
            for e_ in re.split('\\s+', e):
                res.append(e_)
    return res

def aggregate_append(args):
    pops = []
    for i, arg in enumerate(args):
        if arg == '>' and i+1 < len(args) and args[i+1] == '>':
            pops.append(i+1)
            args[i] == '>>'
    for i in reversed(pops):
        args.pop(i)
    return args

def and_or_split(args):
    separators = ['&&', '||', ';', '>']
    separators_re = ['\\s*&&\\s*', '\\s*[|][|]\\s*', '\\s*;\\s*', None]
    #print("args", args)
    for sep, sep_re in zip(separators, separators_re):
        res = []
        for e in args:
            if len(e) > 0 and e[0] == "'":
                res.append(e)
            else:
                if sep == '>':
                    if e in ['2>&1', '1>&2']:
                        res.append(e)
                        continue
                    m1 = re.match('([^>]*)(>[>]?)(.*)', e)
                    m2 = re.match('([^>]*)([12]>[>]?)(.*)', e)
                    if m2:
                        cols = [m2.group(i) for i in range(1,4)]
                    elif m1:
                        cols = [m1.group(i) for i in range(1,4)]
                    else:
                        cols = [e]
                    for col in cols:
                        res.append(col)
                else:
                    cols = re.split(sep_re, e)
                    res.append(cols[0])
                    for col in cols[1:]:
                        res.append(sep)
                        res.append(col)
        args = res
    return args

def exec_split(args):
    # single quote split
    #print(s)
    args = single_quote_split(args)
    args = space_split(args)
    args = and_or_split(args)
    args = [arg for arg in args if arg != '']
    args = [unquote(arg) for arg in args]
    #print(args)
    return args

def test_exec_split():

    group1 = 0

    if group1:
        s = "a'b'c"
        e = ['a','b','c']
        a = exec_split([s])
        assert e == a

    if group1:
        s = "a 'b' c"
        e = ['a','b','c']
        a = exec_split([s])
        assert e == a

    if group1:
        s = "a;'b'&&c"
        e = ['a', ';','b','&&','c']
        a = exec_split([s])
        assert e == a

    if group1:
        s = "oud quc'ponix'atite ngrma'wns'kere ly ate"
        e = ["oud","quc",'ponix',"atite","ngrma",'wns',"kere","ly","ate"]
        a = exec_split([s])
        assert e == a

    if group1:
        s = "and po 'cus ff' chict idke 'bi wons've cog"
        e = ["and", "po", "cus ff", "chict", "idke", "bi wons", "ve", "cog"]
        a = exec_split([s])
        assert e == a

    if group1:
        s = "st; oze 'lica|| ons' pa&&qugaz 'nis ;tre';wasox || paly"
        e = ["st", ";", "oze", "lica|| ons", "pa", "&&", "qugaz", "nis ;tre", ";", "wasox", "||", "paly"]
        a = exec_split([s])
        assert e == a

    if 1:
        s = "echo 1 > test.txt"
        e = ['echo', '1', '>', 'test.txt']
        a = exec_split([s])
        assert e == a

    if 1:
        s = "echo 1> test.txt"
        e = ['echo', '1>', 'test.txt']
        a = exec_split([s])
        assert e == a

    if 1:
        s = "echo 3> test.txt"
        e = ['echo', '3', '>', 'test.txt']
        a = exec_split([s])
        assert e == a

    if 1:
        s = "echo 1 2>&1"
        e = ["echo","1","2>&1"]
        a = exec_split([s])
        assert e == a

    if 1:
        s = "echo 1>>1"
        e = ["echo","1>>", "1"]
        a = exec_split([s])
        assert e == a

    if 1:
        s = "echo 2>>1"
        e = ["echo","2>>", "1"]
        a = exec_split([s])
        assert e == a

    if 1:
        s = "echo 3>>1"
        e = ["echo", "3", ">>", "1"]
        a = exec_split([s])
        assert e == a

    if 1:
        s = "echo 2 >> 1"
        e = ["echo", "2", ">>", "1"]
        a = exec_split([s])
        assert e == a

    print("test_exec_split passed")

test_exec_split()

def split_cmds(args):
    cmd = []
    for e in args:
        if e == '&&' or e == '||' or e == ';':
            if len(cmd) == 0 and e != ';':
                raise ValueError("invalid command")
            yield cmd
            cmd = []
            yield e
        else:
            cmd.append(e)
    if len(cmd) == 0:
        #raise ValueError("invalid command")
        pass
    else:
        yield cmd