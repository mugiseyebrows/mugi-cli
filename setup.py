from setuptools import setup, find_packages

with open('readme.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    packages = find_packages(),
    name = 'mugicli',
    version='0.0.1',
    author="Stanislav Doronin",
    author_email="mugisbrows@gmail.com",
    url='https://github.com/mugiseyebrows/mugi-cli',
    description='Shell utilities resembling coreutils and findutils, small extendable and windows-friendly',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    install_requires = ['python-dateutil'],
    entry_points={
        'console_scripts': [
            'pyfind = mugicli.pyfind:main',
            'pyxargs = mugicli.pyxargs:main',
            'pytouch = mugicli.pytouch:main',
            'pyhead = mugicli.pyhead:main',
            'pytail = mugicli.pytail:main',
            'pygrep = mugicli.pygrep:main',
            'pytime = mugicli.pytime:main',
            'pywc = mugicli.pywc:main',
            'pydu = mugicli.pydu:main',
            'pysed = mugicli.pysed:main',
            'pymtimestat = mugicli.pymtimestat:main',
            'pyextstat = mugicli.pyextstat:main',
            'pyzip = mugicli.pyzip:main',
            'pystart = mugicli.pystart:main',
        ]
    },
)