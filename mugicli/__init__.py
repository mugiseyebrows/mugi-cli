import sys
import re

def read_stdin_text():
    data = sys.stdin.buffer.read()
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        text = data.decode(sys.stdin.encoding)
    return text

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def parse_size(arg):
    m = re.match('^([-+]?[0-9.e]+)+([cwbkmg]?)$', arg, re.IGNORECASE)
    if m is None:
        return None
    size = float(m.group(1))
    prefix = m.group(2)
    return int(size * {'k': 1024, 'm': 1024 * 1024, 'g': 1024 * 1024 * 1024, 'c': 1, 'b': 512, '': 1}[prefix.lower()])