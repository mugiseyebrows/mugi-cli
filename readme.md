# About

Linux shell is very powerful because of shell utils. On Windows you can use bash inside cygwin or msys or gnuwin32 to have similar experience.

But

1. utils don't talk in native paths
2. now you have to take msys/cygwin and batteries with you for your oneliner
3. you cannot easily extend or modify this utils

Aim of this package is to fix all this inconviniences.

1. `mugicli` talks in native paths, pipe it into other applications without doubt
2. `python -m pip install mugicli` and you're done (assuming `Scripts` in `%PATH%`)
3. `mugicli` is writen in less than `2k lines` of `python` code, you can easily change it

Utils supports many of gnu utils arguments, but not all of them as it is not drop-in replacement and will never be.

You can use this package to avoid bash and powershell and still have decent shell experience.

# Applications

## pydu
```
usage: pydu.py [-s] [-h] [--help] [path ...]

prints directories sizes

positional arguments:
  path    path to calculate

optional arguments:
  -s      print only summary
  -h      print in human readible units
  --help

```
## pyextstat
```
usage: pyextstat.py [-h] [-s] [paths ...]

prints extension statistics

positional arguments:
  paths        paths

optional arguments:
  -h, --help   show this help message and exit
  -s, --short  short statistics

```
## pyfind
```
usage: pyfind [conditions] [-exec cmd args {} ;] [-delete]

finds files and dirs that satisfy conditions (predicates)

predicates:
  -mtime DAYS          if DAYS is negative: modified within DAYS days, 
                       if positive modified more than DAYS days ago
  -ctime DAYS          same as -mtime, but when modified metadata not content
  -mmin MINUTES        if MINUTES is negative: modified within MINUTES minutes, 
                       if positive modified more than MINUTES minutes ago
  -cmin MINUTES        same as -mmin, but when modified metadata not content
  -newer PATH/TO/FILE  modified later than PATH/TO/FILE
  -newermt DATETIME    modified later than DATETIME
  -newerct DATETIME    same as -newermt but when modified metadata not content
  -name PATTERN        filename matches PATTERN (wildcard)
  -iname PATTERN       same as -name but case insensitive
  -type d              is directory
  -type f              is file

predicates can be inverted using -not, can be grouped together in boolean expressions 
using -or and -and and parenthesis

examples:
  pyfind -iname *.py -mmin -10
  pyfind -iname *.cpp -or -iname *.h -not ( -iname moc_* -or -iname ui_* )
  pyfind -iname *.h -exec pygrep -H class {} ;
  pyfind -iname *.o -delete
  pyfind -iname *.py | pyxargs pywc -l


```
## pygrep
```
usage: pygrep.py [-i] [-o] [-v] [-H] [-h] [-n] [--help] expr [path ...]

prints matching lines

positional arguments:
  expr
  path

optional arguments:
  -i, --ignore-case     ignore case
  -o, --only-matching
  -v, --invert-match    select non-matching lines
  -H, --with-filename   print file name
  -h, --without-filename
                        do not print file name
  -n, --line-number     print line number
  --help

```
## pyhead
```
usage: pyhead.py [-h] [-n N] [path ...]

prints n lines from head of file

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit
  -n N        number of lines to print

```
## pymtimestat
```
usage: pymtimestat.py [-h] [-r RECENT] [-o OLD] [-a AVERAGE]
                      [-i INCLUDE [INCLUDE ...]] [-e EXCLUDE [EXCLUDE ...]]
                      [path ...]

prints mtime statistics

positional arguments:
  path

optional arguments:
  -h, --help            show this help message and exit
  -r RECENT, --recent RECENT
                        print recently changed files (max(mtime) - mtime <= N)
  -o OLD, --old OLD     print long ago changed files (mtime - min(mtime) <= N)
  -a AVERAGE, --average AVERAGE
                        print files changed within N seconds around average
                        (abs(average(mtime) - mtime) <= N)
  -i INCLUDE [INCLUDE ...], --include INCLUDE [INCLUDE ...]
                        include files glob
  -e EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                        include files glob

```
## pysed
```
usage: pysed.py [-h] [-e E] expr [path ...]

replaces text

positional arguments:
  expr
  path

optional arguments:
  -h, --help  show this help message and exit
  -e E        expression

```
## pystart
```
usage: pystart.py [-h] [--show] path [path ...]

open file in associated application or directory in explorer

positional arguments:
  path        paths to start

optional arguments:
  -h, --help  show this help message and exit
  --show

```
## pytail
```
usage: pytail.py [-h] [-n N] [path ...]

prints n lines from tail of file

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit
  -n N        number of lines to print

```
## pytime
```
usage: pytime program [...args]

measures execution time of application


```
## pytouch
```
usage: pytouch.py [-h] [-d D] path [path ...]

changes mtime to current time or specified time

positional arguments:
  path        target path

optional arguments:
  -h, --help  show this help message and exit
  -d D        datetime

```
## pywc
```
usage: pywc.py [-h] [-l] [-w] [-m] [-c] [path ...]

calculates number or lines words, chars and bytes in files

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit
  -l          print the newline counts
  -w          print the word counts
  -m          print the character counts
  -c          print the byte counts

examples:
  wc -l text.txt

```
## pyxargs
```
usage: pyxargs [-n num] command [args...]

reads arguments from stdin and applies them to command

optional arguments:
-h --help  show this message and exit
-n         split arguments to chunks of n


```
## pyzip
```
usage: pyzip.py [-h] [-o OUTPUT] {a,x,l} zip [sources ...]

appends, extracts and list contents of zip archive

positional arguments:
  {a,x,l}
  zip
  sources

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output directory

```
# Notes
## Escaping

Windows shell (cmd) doesn't expand wildcards so you dont need to put them in quotes, also you dont need to escape parenthesis. Escape symbol for special chars is ^, not \

/dev/null windows alternative is NUL
