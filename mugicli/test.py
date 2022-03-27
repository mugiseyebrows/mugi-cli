import os
import subprocess
import argparse
import textwrap

def get_output_text(cmd):
    outp = subprocess.check_output(cmd.split(' '))
    return outp.decode('utf-8')

def test_pygrep():
        
    with open("1.txt", 'w', encoding='utf-8') as f:
        f.write(textwrap.dedent("""\
                                foo
                                bar
                                baz
                                """))

    with open("2.txt", 'w', encoding='utf-8') as f:
        f.write(textwrap.dedent("""\
                                foo
                                bar
                                baz"""))

    outp = get_output_text("python -m mugicli.pygrep a 1.txt")
    assert(outp == 'bar\nbaz\n')

    outp = get_output_text("python -m mugicli.pygrep A 1.txt")
    assert(outp == '')

    outp = get_output_text("python -m mugicli.pygrep -i A 1.txt")
    assert(outp == 'bar\nbaz\n')

    outp = get_output_text("python -m mugicli.pygrep -h a 1.txt")
    assert(outp == 'bar\nbaz\n')

    outp = get_output_text("python -m mugicli.pygrep -H a 1.txt")
    assert(outp == '1.txt:bar\n1.txt:baz\n')

    outp = get_output_text("python -m mugicli.pygrep -n a 2.txt")
    assert(outp == '2:bar\n3:baz\n')

    outp = get_output_text("python -m mugicli.pygrep -Hn a 2.txt")
    assert(outp == '2.txt:2:bar\n2.txt:3:baz\n')

    outp = get_output_text("python -m mugicli.pygrep a 1.txt 2.txt")
    assert(outp == '1.txt:bar\n1.txt:baz\n2.txt:bar\n2.txt:baz\n')

    outp = get_output_text("python -m mugicli.pygrep a *.txt")
    assert(outp == '1.txt:bar\n1.txt:baz\n2.txt:bar\n2.txt:baz\n')

    outp = get_output_text("python -m mugicli.pygrep -h a *.txt")
    assert(outp == 'bar\nbaz\nbar\nbaz\n')

    outp = get_output_text("python -m mugicli.pygrep -v a *.txt")
    assert(outp == '1.txt:foo\n2.txt:foo\n')

    os.remove("1.txt")
    os.remove("2.txt")

    print("test_pygrep passed")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('prog', choices=['pygrep'])
    args = parser.parse_args()
    if args.prog == 'pygrep':
        test_pygrep()

if __name__ == "__main__":
    main()
    
