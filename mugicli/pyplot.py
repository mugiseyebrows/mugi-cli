import argparse
from ast import parse
from matplotlib import pyplot as plt
import re
from . import read_file_text, read_stdin_text
from functools import partial
import numpy
import dateutil.parser
from .shared import glob_paths_files
from dataclasses import dataclass, field

def parse_date_num(rx, line):
    m = rx.match(line)
    if m:
        return dateutil.parser.parse(m.group(1)), float(m.group(2))

def parse_num_num(rx, line):
    m = rx.match(line)
    if m:
        return float(m.group(2)), float(m.group(2))

class Parser:
    def __init__(self, line):
        date_num = re.compile('^([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\\s+([0-9.e+-]+)$')
        num_num = re.compile('^([0-9.e+-]+)\\s+([0-9.e+-]+)$')
        if date_num.match(line):
            self._parser = partial(parse_date_num, date_num)
        elif num_num.match(line):
            self._parser = partial(parse_num_num, num_num)

    def parse(self, line):
        return self._parser(line)

@dataclass
class State:
    xs: list = field(default_factory=list)
    ys: list = field(default_factory=list)
    parser: Parser = None

def main():
    parser = argparse.ArgumentParser(description='plots data')
    parser.add_argument('path', nargs='*')
    args = parser.parse_args()
    
    state = State()

    def add_line(line):
        line = line.rstrip()
        if state.parser is None:
            state.parser = Parser(line)
        data = state.parser.parse(line)
        if not data is None:
            x, y = data
            state.xs.append(x)
            state.ys.append(y)

    if len(args.path) == 0:
        parser = None
        for line in read_stdin_text().split('\n'):
            add_line(line)
    else:
        for path in glob_paths_files(args.path):
            text = read_file_text(path)
            for line in text.split("\n"):
                add_line(line)

    plt.plot(state.xs, state.ys)
    plt.show()

if __name__ == "__main__":
    main()



