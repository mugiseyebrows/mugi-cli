import os
from setuptools import setup, find_packages

readme_path = os.path.join(os.path.dirname(__file__), 'readme.md')
with open(readme_path, encoding='utf-8') as f:
    long_description = f.read()

setup(
    packages = find_packages(),
    name = 'mugicli',
    version='0.0.29',
    author="Stanislav Doronin",
    author_email="mugisbrows@gmail.com",
    url='https://github.com/mugiseyebrows/mugi-cli',
    description='Shell utilities resembling coreutils and findutils, small extendable and windows-friendly',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    install_requires = ['python-dateutil','bashrange','chardet'],
    entry_points={
        'console_scripts': [
            'pycat = mugicli.pycat:main',
            'pycol = mugicli.pycol:main',
            'pycwd = mugicli.pycwd:main',
            'pydos2unix = mugicli.pydos2unix:main',
            'pydu = mugicli.pydu:main',
            'pyecho = mugicli.pyecho:main',
            'pyexec = mugicli.pyexec:main',
            'pyextstat = mugicli.pyextstat:main',
            'pyfalse = mugicli.pyfalse:main',
            'pyfind = mugicli.pyfind:main',
            'pygrep = mugicli.pygrep:main',
            'pyhead = mugicli.pyhead:main',
            'pyiconv = mugicli.pyiconv:main',
            'pyls = mugicli.pyls:main',
            'pymd5sum = mugicli.pymd5sum:main',
            'pymtime = mugicli.pymtime:main',
            'pymtimestat = mugicli.pymtimestat:main',
            'pynmap = mugicli.pynmap:main',
            'pynth = mugicli.pynth:main',
            'pyplot = mugicli.pyplot:main',
            'pyrandom = mugicli.pyrandom:main',
            'pyfor = mugicli.pyfor:main',
            'pysed = mugicli.pysed:main',
            'pyseq = mugicli.pyseq:main',
            'pysetpath = mugicli.pysetpath:main',
            'pysha1sum = mugicli.pysha1sum:main',
            'pysha224sum = mugicli.pysha224sum:main',
            'pysha256sum = mugicli.pysha256sum:main',
            'pysha384sum = mugicli.pysha384sum:main',
            'pysha512sum = mugicli.pysha512sum:main',
            'pysleep = mugicli.pysleep:main',
            'pysort = mugicli.pysort:main',
            'pystart = mugicli.pystart:main',
            'pytail = mugicli.pytail:main',
            'pytime = mugicli.pytime:main',
            'pytmp = mugicli.pytmp:main',
            'pytouch = mugicli.pytouch:main',
            'pytr = mugicli.pytr:main',
            'pytree = mugicli.pytree:main',
            'pytrue = mugicli.pytrue:main',
            'pyuniq = mugicli.pyuniq:main',
            'pyunix2dos = mugicli.pyunix2dos:main',
            'pywc = mugicli.pywc:main',
            'pyxargs = mugicli.pyxargs:main',
            'pyxxd = mugicli.pyxxd:main',
            'pyzip = mugicli.pyzip:main',
        ]
    },
)