import sys

def print_help():
    print("""usage: pyprintcmd [--help] args...
prints args to stdout as python array
""")

def main():
    args = sys.argv[1:]
    if args == ['--help']:
        print_help()
        return
    print(args)
    
if __name__ == "__main__":
    main()