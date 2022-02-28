from setuptools import setup, find_packages

with open('readme.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    packages = find_packages(),
    name = 'mugicli',
    version='0.0.3',
    author="Stanislav Doronin",
    author_email="mugisbrows@gmail.com",
    url='https://github.com/mugiseyebrows/mugi-cli',
    description='Shell utilities resembling coreutils and findutils, small extendable and windows-friendly',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    install_requires = ['python-dateutil'],
    entry_points={
        'console_scripts': [
            'pycat = mugicli.pycat:main',
            'pycol = mugicli.pycol:main',
            'pydos2unix = mugicli.pydos2unix:main',
            'pydu = mugicli.pydu:main',
            'pyecho = mugicli.pyecho:main',
            'pyextstat = mugicli.pyextstat:main',
            'pyfind = mugicli.pyfind:main',
            'pygrep = mugicli.pygrep:main',
            'pyhead = mugicli.pyhead:main',
            'pyls = mugicli.pyls:main',
            'pymd5sum = mugicli.pymd5sum:main',
            'pymtime = mugicli.pymtime:main',
            'pymtimestat = mugicli.pymtimestat:main',
            'pysed = mugicli.pysed:main',
            'pyseq = mugicli.pyseq:main',
            'pysha1sum = mugicli.pysha1sum:main',
            'pysha224sum = mugicli.pysha224sum:main',
            'pysha256sum = mugicli.pysha256sum:main',
            'pysha384sum = mugicli.pysha384sum:main',
            'pysha512sum = mugicli.pysha512sum:main',
            'pysort = mugicli.pysort:main',
            'pystart = mugicli.pystart:main',
            'pytail = mugicli.pytail:main',
            'pytime = mugicli.pytime:main',
            'pytmp = mugicli.pytmp:main',
            'pytouch = mugicli.pytouch:main',
            'pyuniq = mugicli.pyuniq:main',
            'pyunix2dos = mugicli.pyunix2dos:main',
            'pywc = mugicli.pywc:main',
            'pyxargs = mugicli.pyxargs:main',
            'pyxxd = mugicli.pyxxd:main',
            'pyzip = mugicli.pyzip:main',
        ]
    },
)