from . import predicate
from .tok import T, TOK, TOK_AS_STR, tok_pred, tok_pred_nargs, tok_pred_noargs, tok_type_as_string
from .types import Pred

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

NODE_CONSTRUCTORS = {
    TOK.op_par: NodeOpPar,
    TOK.cl_par: NodeClPar,
    TOK.and_: NodeAnd,
    TOK.or_: NodeOr,
    TOK.not_: NodeNot,
}

class NodePred:

    def __init__(self, tokens):
        self._tokens = tokens
        type, arg, val = self._type_arg_val()
        #print(self)
        #print("type", type, "arg", arg, "val", val)

    def __repr__(self) -> str:
        type_, arg, val = self._type_arg_val()
        type_str = TOK_AS_STR[type_]
        if len(self._tokens) == 2:
            return 'NodePred({} {} {})'.format(type_str, arg, val)
        else:
            return 'NodePred(-not {} {} {})'.format(type_str, arg, val)

    def _type_arg_val(self):
        tokens = self._tokens

        if tokens[0].type == TOK.not_:
            type = tokens[1].type
            nargs = len(tokens) - 2
        else:
            nargs = len(tokens) - 1
            type = tokens[0].type

        if type in tok_pred_nargs or type == TOK.mdate:
            val = [e.val for e in tokens[-nargs:]]
            arg = [e.cont for e in tokens[-nargs:]]
        else:
            val = tokens[-1].val
            arg = tokens[-1].cont
        return type, arg, val

    def eval(self, name, path, is_dir):

        exp = False if self._tokens[0].type == TOK.not_ else True
        type_, arg, val = self._type_arg_val()

        if arg is None:
            return None

        res = {
            TOK.type: predicate.type,
            TOK.mmin: predicate.mmin,
            TOK.iname: predicate.iname,
            TOK.name: predicate.name,
            TOK.newer: predicate.newer,
            TOK.newermt: predicate.newermt,
            TOK.newerct: predicate.newerct,
            TOK.ctime: predicate.ctime,
            TOK.mtime: predicate.mtime,
            TOK.size: predicate.size,
            TOK.grep: predicate.grep,
            TOK.igrep: predicate.igrep,
            TOK.bgrep: predicate.bgrep,
            TOK.path: predicate.path,
            TOK.ipath: predicate.ipath,
            TOK.mdate: predicate.mdate,
            TOK.cpptmp: predicate.cpptmp,
            TOK.docgrep: predicate.docgrep,
            TOK.xlgrep: predicate.xlgrep,
            TOK.gitdir: predicate.gitdir
        }[type_](name, path, is_dir, arg, val)

        if res is None:
            return None
        return res == exp


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

    def eval(self, name, path, is_dir):
        for child in self._children:
            res = child.eval(name, path, is_dir)
            if res in [None, False]:
                return res
        # all True
        return True

    def __repr__(self):
        return "NodeGroupAnd({})".format(repr(self._children))

class NodeGroup:
    pass

class NodeGroupOr:
    def __init__(self, nodes):
        self._children = normalize(nodes)
    
    def eval(self, name, path, is_dir):
        for child in self._children:
            res = child.eval(name, path, is_dir)
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

    def eval(self, name, path, is_dir):
        res = self._child.eval(name, path, is_dir)
        if res is None:
            return None
        return not res

    def __repr__(self):
        return "NodeGroupNot({})".format(repr(self._child))

def pred_token_index(tokens):
    for i, token in enumerate(tokens):
        if not isinstance(token, T):
            continue
        if token.type in tok_pred:
            return i
    return -1

def max_level(tree):
    level = -1
    for e in tree:
        if isinstance(e, tuple):
            level = max(level, e[1])
    return level

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

def without_or(nodes):
    return [node for node in nodes if not isinstance(node, NodeOr)]

def strip_level(tokens):
    return [e[0] if isinstance(e, tuple) else e for e in tokens]

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

def expr_to_pred(expr) -> tuple[NodeGroup, Pred]:

    while True:
        i = pred_token_index(expr)
        if i > -1:
            if i > 0 and isinstance(expr[i-1], T) and expr[i-1].type == TOK.not_:
                head = i-1
            else:
                head = i
            
            if expr[i].type in tok_pred_nargs:
                nargs = 0
                for j in range(i+1, len(expr)):
                    if expr[j].type == TOK.arg:
                        nargs += 1
                    else:
                        break
            elif expr[i].type in tok_pred_noargs:
                nargs = 0
            else:
                nargs = 1
            expr = expr[:head] + [NodePred(expr[head: i+nargs+1])] + expr[i+nargs+1:]
            
        else:
            break

    for i, tok in enumerate(expr):
        if isinstance(tok, T):
            if tok.type not in NODE_CONSTRUCTORS:
                raise ValueError("unexpected token type {}".format(tok_type_as_string(tok.type)))
            expr[i] = NODE_CONSTRUCTORS[tok.type]()

    expr = [e for e in expr if not isinstance(e, NodeAnd)]

    tree = []

    level = 0

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
        return None, lambda name, path, is_dir: True
    
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

    return tree, lambda name, path, is_dir: tree.eval(name, path, is_dir)