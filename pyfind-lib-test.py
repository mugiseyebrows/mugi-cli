import asyncio
from mugicli.pyfind.lib import find

def main():

    def callback(root, name, path, is_dir):
        print("callback", root, name, path, is_dir)

    find('D:\\dev').maxdepth(3).with_exts('cpp', 'h').mtime(-2).first(5).run(callback)

if __name__ == "__main__":
    main()