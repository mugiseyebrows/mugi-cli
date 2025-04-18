from .headtail import read_head_lines, read_head_chars, app

def main():
    app(read_head_lines, read_head_chars)

if __name__ == "__main__":
    main()