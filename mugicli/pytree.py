import argparse
import os
import re
from . import print_utf8, walk, include_exclude

def split_path(path):
    parts = re.split('[/\\\\]', path)
    if re.match('^[a-z]:$',parts[0],re.IGNORECASE):
        parts[0] = parts[0] + "\\"
    return parts

class Node:
    def __init__(self, name = None, level = 0, children = None):
        self._name = name
        if children is None:
            children = []
        self._children = children
        self._level = level
        self._last_child = False

    def name(self):
        return self._name

    def level(self):
        return self._level

    def is_last_child(self):
        return self._last_child

    def children(self):
        return self._children

    def child_count(self):
        tot = 0
        for c in self._children:
            tot += 1 + c.child_count()
        return tot

    def add_child(self, name, level):
        if len(self._children):
            self._children[-1].set_last_child(False)
        node = Node(name, level)
        node.set_last_child(True)
        self._children.append(node)

    def set_last_child(self, value):
        self._last_child = value

    def get_child(self, name):
        for c in self._children:
            if c.name() == name:
                return c
    
    def __repr__(self):
        return "Node({},{})".format(self._name, repr(self._children))

class Tree:
    def __init__(self, base, node = None):
        self._base = base
        if node is None:
            node = Node()
        self._node = node

    def __repr__(self):
        return "Tree({}, {})".format(self._base, repr(self._node))

    def to_str(self, show_dot = True):
        node = self._node

        def append(node, res):
            if node.name() is not None:
                res.append(node)
            for c in node.children():
                append(c, res)
            
        res = []
        append(self._node, res)

        lines = []

        for node in res:
            line = ""
            for n in range(node.level() + 1):
                line += "    "
            line = line + node.name()
            lines.append(line)

        def repl_char(s, ix, ss):
            return s[:ix] + ss + s[ix + len(ss):]

        max_level = max([node.level() for node in res])

        for level in range(max_level + 1):
            has_more_children = True
            for i, node in enumerate(res):
                if node.level() == level:
                    if node.is_last_child():
                        s = "└──"
                        has_more_children = False
                    else:
                        s = "├──"
                        has_more_children = True
                    lines[i] = repl_char(lines[i], level * 4, s)
                elif node.level() > level and has_more_children:
                    lines[i] = repl_char(lines[i], level * 4, "│")

        return self._base + "\n" + "\n".join(lines)
            
    def add(self, root, f):
        relpath = os.path.relpath(os.path.join(root, f), self._base)
        
        basename = os.path.basename(relpath)
        dirname = split_path(os.path.dirname(relpath))

        node = self._node
        level = 0
        if dirname == ['']:
            node.add_child(basename, level)
        else:
            for d in dirname:
                node = node.get_child(d)
                level += 1
            """
            if node is None:
                print("root {} f {} tree {}".format(root, f, repr(self._node)))
            """
            node.add_child(basename, level)

        #print("relpath", relpath, "basename", basename, "dirname", dirname)
        

def main():
    # todo inlcude exclude clildless dirs
    # todo sort alphabetically, dirs first files first
    parser = argparse.ArgumentParser()
    parser.add_argument('-L','--level', type=int, help='depth', default=0)
    parser.add_argument('-i', '--include', nargs='+', help='include files globs')
    parser.add_argument('-e', '--exclude', nargs='+', help='include files globs')
    parser.add_argument('path')

    args = parser.parse_args()
    tree = Tree(args.path)
    for root, dirs, files in walk(args.path, maxdepth=args.level):
        for f in files:
            if include_exclude(args.include, args.exclude, f):
                tree.add(root, f)
        for d in dirs:
            tree.add(root, d)

    print_utf8(tree.to_str())

if __name__ == "__main__":
    main()