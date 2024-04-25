import argparse

def main():
    parser = argparse.ArgumentParser(prog='pyfalse', description='exits with code 1')
    parser.parse_args()
    exit(1)

if __name__ == "__main__":
    main()