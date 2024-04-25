import re
import os
import subprocess
base = os.path.dirname(__file__)

#progs = [os.path.splitext(n[2:])[0] for n in os.listdir('mugicli') if re.match('py.*\\.py', n)]

progs = []
src = os.path.join(base, 'mugicli')
for n in os.listdir(src):
    p = os.path.join(src, n)
    if os.path.isdir(p) and n.startswith('py'):
        progs.append(n[2:])
    if os.path.isfile(p) and n.startswith('py'):
        progs.append(os.path.splitext(n)[0][2:])

progs.sort()

#print('progs', progs); exit()

console_scripts = ["'py{} = mugicli.py{}:main',".format(n, n) for n in progs]

path = os.path.join(base, 'tmp.txt')

with open(path, 'w', encoding='utf-8') as f:
    f.write("\n".join(console_scripts))

#print(progs)

helps = dict()

for prog in progs:
    print(prog)
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

def repl(m):
    line = m.group(0)
    name_py = m.group(1)
    name = os.path.splitext(name_py)[0]
    return line.replace(name_py, name)

path = os.path.join(base, 'readme.md')
with open(path, 'w', encoding='utf-8') as f:
    f.write(data['about'])
    f.write("# Applications\n\n")
    for prog in progs:
        prog_ = 'py' + prog
        f.write("## {}\n```\n".format(prog_))

        cont = helps[prog].decode('utf-8').replace('\r\n','\n') + '\n'
        cont = re.sub('usage: ([a-z0-9_]+\\.py)', repl, cont)

        f.write(cont)
        f.write('```\n')
    f.write("# Notes\n")
    f.write(data['escaping'])