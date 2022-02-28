import os
import textwrap
algs = [
    'md5',
    'sha1',
    'sha224',
    'sha256',
    'sha384',
    'sha512',
]
base = os.path.dirname(__file__)
for alg in algs:
    path = os.path.join(base, 'mugicli', 'py{}sum.py'.format(alg))
    with open(path,'w',encoding='utf-8') as f:
        f.write(textwrap.dedent("""\
        from . import files_hash_main
        def main():
            files_hash_main('{}')
        if __name__ == "__main__":
            main()
        """.format(alg)))

"""
path = os.path.join(base, 'tmp.txt')
with open(path, 'w', encoding='utf-8') as f:
    text = "\n".join(["'py{}sum = mugicli.py{}sum:main',".format(alg, alg) for alg in algs])
    f.write(text)
"""
