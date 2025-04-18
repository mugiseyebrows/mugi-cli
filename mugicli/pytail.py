from .headtail import read_tail_lines, read_tail_chars, app

def main():
    app(read_tail_lines, read_tail_chars)

if __name__ == "__main__":
    main()