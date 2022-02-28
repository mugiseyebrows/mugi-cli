import re
import os
import subprocess
base = os.path.dirname(__file__)

progs = [os.path.splitext(n[2:])[0] for n in os.listdir('mugicli') if re.match('py.*\\.py', n)]

console_scripts = ["'py{} = mugicli.py{}:main',".format(n, n) for n in progs]

path = os.path.join(base, 'tmp.txt')

with open(path, 'w', encoding='utf-8') as f:
    f.write("\n".join(console_scripts))

#print(progs)

helps = dict()

for prog in progs:
    helps[prog] = subprocess.check_output(["python","-m","mugicli.py" + prog,"--help"])

data = dict()
for n in os.listdir('.'):
    if os.path.splitext(n)[1] not in ['.md']:
        continue
    b = os.path.splitext(n)[0]
    if b == 'readme':
        continue
    with open(n, encoding='utf-8') as f:
        data[b] = f.read()

path = os.path.join(base, 'readme.md')
with open(path, 'w', encoding='utf-8') as f:
    f.write(data['about'])
    f.write("# Applications\n\n")
    for prog in progs:
        prog_ = 'py' + prog
        f.write("## {}\n```\n".format(prog_))
        f.write(helps[prog].decode('utf-8').replace('\r\n','\n') + '\n')
        f.write('```\n')
    f.write("# Notes\n")
    f.write(data['escaping'])