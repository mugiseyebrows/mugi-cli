from ast import parse
import os
import argparse
import glob
import subprocess
import shutil

def find_explorer():
    # todo other platforms
    explorer = shutil.which('explorer')
    if explorer is not None:
        return explorer

    root = os.environ['SystemRoot']
    path = os.path.join(root, "explorer.exe")
    if os.path.exists(path):
        return path
    path = os.path.join(root, "system32", "explorer.exe")
    if os.path.exists(path):
        return path

def main():
    parser = argparse.ArgumentParser(description='opens file in associated application or directory in explorer')
    parser.add_argument('path', nargs='+', help='paths to start')
    parser.add_argument('--show', action='store_true')
    args = parser.parse_args()

    paths = []

    for path in args.path:
        if glob.has_magic(path):
            for path_ in glob.glob(path):
                paths.append(path_)
        else:
            paths.append(path)

    if args.show:
        explorer = find_explorer()
    
    for path in paths:
        if args.show:
            subprocess.run([explorer, "/select,", path])
        else:
            os.startfile(path)

if __name__ == "__main__":
    main()