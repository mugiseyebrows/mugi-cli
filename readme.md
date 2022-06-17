# About

Linux shell is very powerful because of shell utils. On Windows you can use bash inside cygwin or msys or gnuwin32 to have similar experience.

But

1. utils don't talk in native paths
2. now you have to take msys/cygwin and batteries with you for your oneliner
3. you cannot easily extend or modify this utils

Aim of this package is to fix all this inconviniences.

1. `mugicli` talks in native paths, pipe it into other applications without doubt
2. `python -m pip install mugicli` and you're done (assuming `Scripts` in `%PATH%`)
3. `mugicli` is writen in less than `3k lines` of `python` code, you can easily change it

Utils support many of gnu utils arguments, but not all of them as it is not drop-in replacement and will never be.

You can use this package to avoid bash and powershell and still have decent shell experience.

# Applications

## pycat
```
usage: pycat [-h] [--text] path [path ...]

prints file to stdout

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit
  --text, -t

```
## pycol
```
usage: pycol [-h] [-n N [N ...]] [path ...]

extracts and prints specific columns

positional arguments:
  path

optional arguments:
  -h, --help    show this help message and exit
  -n N [N ...]  column number

```
## pycwd
```
usage: pycwd [-h] [--help]

prints current working directory


```
## pydos2unix
```
usage: pydos2unix [-h] [path ...]

converts line endings from dos to unix (\r\n -> \n)

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pydu
```
usage: pydu [-s] [-h] [--help] [path ...]

prints directories sizes

positional arguments:
  path    path to calculate

optional arguments:
  -s      print only summary
  -h      print in human readible units
  --help

```
## pyecho
```
usage: pyecho [-e] [-n] [args...]

prints text to stdout

optional arguments:
-h --help  show this message and exit
-e         decode escape sequences
-n         do not print newline


```
## pyextstat
```
usage: pyextstat [-h] [-s] [path ...]

prints file extension statistics

positional arguments:
  path         paths

optional arguments:
  -h, --help   show this help message and exit
  -s, --short

```
## pyfind
```
usage: pyfind [PATHS] [OPTIONS] [CONDITIONS] [-exec cmd args {} ;] [-delete]

finds files and dirs that satisfy conditions (predicates)

options:
  -maxdepth NUMBER     walk no deeper than NUMBER levels
  -output PATH         output to file instead of stdout

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
  -path PATTERN        file path matches PATTERN
  -ipath PATTERN       same as -path but case insensitive
  -cont PATTERN        file contains PATTERN
  -icont PATTERN       same as -cont but case insensitive
  -bcont PATTERN       same as -cont but PATTERN is binary expression
  -type d              is directory
  -type f              is file
  -cdup NUMBER         print (or perform action) parent path (strip NUMBER 
                       trailing components from path)
  -first NUMBER        print (or perform action) first NUMBER found items
  -last NUMBER         print (or perform action) last NUMBER found items

predicates can be inverted using -not, can be grouped together in boolean expressions 
using -or and -and and parenthesis

examples:
  pyfind -iname *.py -mmin -10
  pyfind -iname *.cpp -or -iname *.h -not ( -iname moc_* -or -iname ui_* )
  pyfind -iname *.h -exec pygrep -H class {} ;
  pyfind -iname *.o -delete
  pyfind -iname *.py | pyxargs pywc -l
  pyfind D:\dev -iname .git -type d -cdup 1

note:
  python treats trailing slash before quotation mark as escape sequence 
  so in order to input root drive paths you need to not use quotation marks 
  or double trailing slash
  correct: "C:\\" C:\ incorrect: "C:\"


```
## pygrep
```
usage: pygrep [-i] [-o] [-v] [-H] [-h] [-n] [--help] expr [path ...]

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
usage: pyhead [-h] [-n N] [path ...]

prints n lines from head of file

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit
  -n N        number of lines to print

```
## pyls
```
usage: pyls [-h] [path ...]

lists directory

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pymd5sum
```
usage: pymd5sum [-h] [path ...]

prints md5 hashsum of file

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pymtime
```
usage: pymtime [-h] [path ...]

prints mtime of file

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pymtimestat
```
usage: pymtimestat [-h] [-r RECENT] [-o OLD] [-a AVERAGE]
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
## pyplot
```
usage: pyplot [-h] [path ...]

plots data

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pysed
```
usage: pysed [-h] [-e E] expr [path ...]

replaces text

positional arguments:
  expr
  path

optional arguments:
  -h, --help  show this help message and exit
  -e E        expression

```
## pyseq
```
Print numbers from FIRST to LAST with INCREMENT
seq LAST
seq FIRST LAST
seq FIRST INCREMENT LAST


```
## pysha1sum
```
usage: pysha1sum [-h] [path ...]

prints sha1 hashsum of file

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pysha224sum
```
usage: pysha224sum [-h] [path ...]

prints sha224 hashsum of file

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pysha256sum
```
usage: pysha256sum [-h] [path ...]

prints sha256 hashsum of file

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pysha384sum
```
usage: pysha384sum [-h] [path ...]

prints sha384 hashsum of file

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pysha512sum
```
usage: pysha512sum [-h] [path ...]

prints sha512 hashsum of file

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pysort
```
usage: pysort [-h] [--numeric-sort] [--reverse] [--random-sort] [--unique]
                 [path ...]

sorts lines

positional arguments:
  path

optional arguments:
  -h, --help          show this help message and exit
  --numeric-sort, -n
  --reverse, -r
  --random-sort, -R
  --unique, -u

```
## pystart
```
usage: pystart [-h] [--show] path [path ...]

opens file in associated application or directory in explorer

positional arguments:
  path        paths to start

optional arguments:
  -h, --help  show this help message and exit
  --show

```
## pytail
```
usage: pytail [-h] [-n N] [path ...]

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
## pytmp
```
usage: pytmp [-h] [-p PRINT [PRINT ...]] [-i INPUT [INPUT ...]] [-o OUTPUT]
                [--suffix SUFFIX]

temporary file helper

optional arguments:
  -h, --help            show this help message and exit
  -p PRINT [PRINT ...], --print PRINT [PRINT ...]
                        print filenames
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        input data from file
  -o OUTPUT, --output OUTPUT
                        output data to file
  --suffix SUFFIX

examples:
    pyecho -e 3\n1\n2 | pytmp -o foo
    pytmp -i foo | pysort
    pytmp -p foo | pyxargs pycat 

```
## pytouch
```
usage: pytouch [-h] [-d D] path [path ...]

changes mtime to current time or specified time

positional arguments:
  path        target path

optional arguments:
  -h, --help  show this help message and exit
  -d D        datetime or relative time in format [+-]NUM[d|h|m|s] format

```
## pytree
```
usage: pytree [-h] [-L LEVEL] [-i INCLUDE [INCLUDE ...]]
                 [-e EXCLUDE [EXCLUDE ...]]
                 path

positional arguments:
  path

optional arguments:
  -h, --help            show this help message and exit
  -L LEVEL, --level LEVEL
                        depth
  -i INCLUDE [INCLUDE ...], --include INCLUDE [INCLUDE ...]
                        include files globs
  -e EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                        include files globs

```
## pyuniq
```
usage: pyuniq [-h] [--count] [--repeated] [--unique] [path ...]

prints unique or nonunique lines from sorted array of lines

positional arguments:
  path

optional arguments:
  -h, --help      show this help message and exit
  --count, -c
  --repeated, -d
  --unique, -u

```
## pyunix2dos
```
usage: pyunix2dos [-h] [path ...]

converts line endings from unix to dos (\n -> \r\n)

positional arguments:
  path

optional arguments:
  -h, --help  show this help message and exit

```
## pywc
```
usage: pywc [-h] [-l] [-w] [-m] [-c] [path ...]

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
usage: pyxargs [-L NUM] [-I VAR] command [args...]

reads arguments from stdin and applies them to command

optional arguments:
  -h --help  show this message and exit
  -L NUM     split arguments to chunks of N args
  -I VAR     replace VAR with arg (assumes -L 1)



```
## pyxxd
```
usage: pyxxd [-h] [-s SEEK] [-l LEN] [path ...]

prints file as hex

positional arguments:
  path

optional arguments:
  -h, --help            show this help message and exit
  -s SEEK, --seek SEEK  start at offset
  -l LEN, --len LEN     number of bytes to print

```
## pyzip
```
usage: pyzip [-h] [-o OUTPUT] [-m {deflate,d,lzma,l,bzip2,b,store,s}]
                [-l L] [--base BASE] [--dir DIR] [--list LIST] [-s] [-v]
                {a,x,l} zip [sources ...]

appends, extracts and list contents of zip archive

positional arguments:
  {a,x,l}               add extract list
  zip
  sources

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output directory
  -m {deflate,d,lzma,l,bzip2,b,store,s}
                        compression method
  -l L                  compression level 0..9 for deflate (0 - best speed, 9
                        - best compression) 1..9 for bzip2, has no effect if
                        method is store or lzma
  --base BASE           base directory
  --dir DIR             prepend directory to path
  --list LIST           path to list of files
  -s, --silent
  -v, --verbose

```
# Notes
## Escaping

Windows shell (cmd) doesn't expand wildcards so you dont need to put them in quotes, also you dont need to escape parenthesis. Escape symbol for special chars is ^, not \

/dev/null windows alternative is NUL
