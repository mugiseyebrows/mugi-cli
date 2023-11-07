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

def and_or_split(args):
    separators = ['&&', '||', ';']
    separators_re = ['\\s*&&\\s*', '\\s*[|][|]\\s*', '\\s*;\\s*']
    #print("args", args)
    for sep, sep_re in zip(separators, separators_re):
        res = []
        for e in args:
            if len(e) > 0 and e[0] == "'":
                res.append(e)
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

    if 1:
        s = "a'b'c"
        e = ['a','b','c']
        a = exec_split([s])
        assert e == a

    if 1:
        s = "a 'b' c"
        e = ['a','b','c']
        a = exec_split([s])
        assert e == a

    if 1:
        s = "a;'b'&&c"
        e = ['a', ';','b','&&','c']
        a = exec_split([s])
        assert e == a

    if 1:
        s = "oud quc'ponix'atite ngrma'wns'kere ly ate"
        e = ["oud","quc",'ponix',"atite","ngrma",'wns',"kere","ly","ate"]
        a = exec_split([s])
        assert e == a

    if 1:
        s = "and po 'cus ff' chict idke 'bi wons've cog"
        e = ["and", "po", "cus ff", "chict", "idke", "bi wons", "ve", "cog"]
        a = exec_split([s])
        assert e == a

    if 1:
        s = "st; oze 'lica|| ons' pa&&qugaz 'nis ;tre';wasox || paly"
        e = ["st", ";", "oze", "lica|| ons", "pa", "&&", "qugaz", "nis ;tre", ";", "wasox", "||", "paly"]
        a = exec_split([s])
        assert e == a

    print("test_exec_split passed")

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