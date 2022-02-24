import sys

def read_stdin_text():
    data = sys.stdin.buffer.read()
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        text = data.decode(sys.stdin.encoding)
    return text
