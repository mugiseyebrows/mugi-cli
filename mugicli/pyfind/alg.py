from shortwalk import walk
import os
from .action import ActionBase
from .types import ExtraArgs

def walk_all(paths, pred, action: ActionBase, extraArgs: ExtraArgs):
    executed = 0

    if extraArgs.first is not None:
        need_to_stop = lambda: executed >= extraArgs.first
    else:
        need_to_stop = lambda: False

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