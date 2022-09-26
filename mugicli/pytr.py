import argparse
from . import read_stdin_text, print_utf8
from bashrange import expand_args

def main():

    example_text = """examples:
  echo %PATH% | pytr ";" "\\n" | pygrep -i conda | pytr "\\n" ";"
  echo %PATH% | pytr ";" "\\n" | pygrep -i conda | pysed s,%USERPROFILE%,^%USERPROFILE^%,r | pytr "\\n" ";"
"""

    parser = argparse.ArgumentParser(description="reads stdin and replaces chars with another chars", prog="pytr", epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('match', help='chars to find')
    parser.add_argument('replacement', help='replacement chars')
    args = parser.parse_args(expand_args())

    match = args.match.encode('utf-8').decode('unicode_escape')
    replacement = args.replacement.encode('utf-8').decode('unicode_escape')
    repl = {m:r for m,r in zip(match, replacement)}
    
    if len(match) != len(replacement):
        raise ValueError('len(args.match) != len(args.replacement)')

    text = read_stdin_text()
    res = "".join([repl.get(c, c) for c in text])
    print_utf8(res)
    

if __name__ == "__main__":
    main()