# About

Linux shell is very powerful because of shell utils. On Windows you can use bash inside cygwin or msys or gnuwin32 to have similar experience.

But

1. utils don't talk in native paths
2. now you have to take msys/cygwin and batteries with you for your oneliner
3. you cannot easily extend or modify this utils

Aim of this package is to fix all this inconviniences.

1. `mugicli` talks in native paths, pipe it into other applications without doubt
2. `python -m pip install mugicli` and you're done (assuming `Scripts` in `%PATH%`)
3. `mugicli` is writen in less than `5k lines` of `python` code, you can easily change it

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
usage: pycwd [-h]

prints current working directory

optional arguments:
  -h, --help  show this help message and exit

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
usage: pyextstat [-s] [--help] [-h] [--order {s,c,size,count}] [--skip-git]
                    [-X]
                    [path ...]

prints file extension statistics

positional arguments:
  path                  paths

optional arguments:
  -s, --short           show short list
  --help                show help
  -h                    human readable sizes
  --order {s,c,size,count}, -o {s,c,size,count}
                        sort order
  --skip-git
  -X, --xargs           read paths from stdin

```
## pyfind
```
usage: pyfind [PATHS] [OPTIONS] [CONDITIONS] [-exec|-aexec cmd args {} ;] [-delete]

finds files and dirs that satisfy conditions (predicates) and executes action or prints path

options:
  -maxdepth NUMBER     walk no deeper than NUMBER levels
  -output PATH         output to file instead of stdout
  -append              append to file instead of rewrite
  -abspath             print absolute paths
  -conc NUMBER         concurrency limit for -aexec

actions:
  -delete              delete matched file
  -exec                execute command(s)
  -aexec               execute command(s) concurrently

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

binds:
  {}         path to file
  {path}     path to file
  {nameext}  name with extension
  {name}     name without extension

examples:
  pyfind -iname *.py -mmin -10
  pyfind -iname *.cpp *.h -not ( -iname moc_* ui_* )
  pyfind -iname *.h -exec pygrep -H class {} ;
  pyfind -iname *.o -delete
  pyfind -iname *.py | pyxargs pywc -l
  pyfind D:\dev -iname .git -type d -cdup 1
  pyfind -iname *.dll -cdup 1 -abspath | pysetpath -o env.bat
  pyfind -iname *.mp3 -conc 4 -aexec ffmpeg -i {} {name}.wav ;

note:
  ";" in cmd does not work as command separator so you dont have to escape it
  although you can if you want.
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
## pyiconv
```
usage: pyiconv [-h] [-f FROM] [-t TO]

converts text from one encoding to another

optional arguments:
  -h, --help            show this help message and exit
  -f FROM, --from FROM
  -t TO, --to TO

examples:
  tasklist | pyiconv -f cp866 | pygrep python

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
## pyrepeat
```

usage: pyrepeat [-h] [--help] [--forever] [-c COUNT] [--count COUNT] [-t SECONDS] [--timeout SECONDS] program

optional arguments:
  -c, --count COUNT      run command COUNT times
  -t, --timeout SECONDS  sleep SECONDS between 

examples:
  pyrepeat -c 100 -t 1 tasklist "|" pyiconv -f cp866 "|" pygrep python

runs command(s) n times


```
## pysed
```
usage: pysed [-h] [-e E] expr [path ...]

replaces text according to expressions

positional arguments:
  expr
  path

optional arguments:
  -h, --help  show this help message and exit
  -e E        expression

examples:
  echo foobar | pysed s,bar,baz,
  echo foobar | pysed -e s,bar,baz, -e s,foo,qix,
  echo %PATH% | pysed s,%USERPROFILE%,^%USERPROFILE^%,r

note:
  use r flag to disable escape sequences interpretation (as in paths)

```
## pyseq
```
Print numbers from FIRST to LAST with INCREMENT
seq LAST
seq FIRST LAST
seq FIRST INCREMENT LAST


```
## pysetpath
```
usage: pysetpath [-h] [-o OUTPUT] [-a] [-p] [-r] [-X] [-g GREP [GREP ...]]
                 [-w WHICH [WHICH ...]] [-u]

reads PATH env variable (or dirs from stdin) and prints set path expression

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output path
  -a, --append
  -p, --prepend
  -r, --reset
  -X, --xargs           read paths from stdin
  -g GREP [GREP ...], --grep GREP [GREP ...]
                        filter paths by patterns
  -w WHICH [WHICH ...], --which WHICH [WHICH ...]
                        add executable path
  -u, --user-profile    replace %USERPROFILE% value with variable name

examples:
  pysetpath -g conda -o conda-env.bat
  pysetpath -w gcc cmake ninja -o mingw-env.bat
  pyfind -type d -name bin -abspath | pysetpath --xargs -o env.bat

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
## pysleep
```
usage: pysleep [-h] [-p PRINT] time [time ...]

sleeps for TIME seconds

positional arguments:
  time

optional arguments:
  -h, --help            show this help message and exit
  -p PRINT, --print PRINT
                        print reminding time

examples:
  pysleep 1m && taskkill 
  pysleep 10 20
  pysleep 60 --print 10

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

usage: pytime program [-h] [--help] [-s SECONDS] [--stat SECONDS] [-p PATH] [--path PATH]

runs program and measures execution time, memory and cpu usage

optional arguments:
  -s SECONDS, --stat SECONDS   measure cpu and memory usage, 
                               take samples with interval of SECONDS
  -p PATH, --path PATH         save cpu and memory stats in file PATH
  -o, --online                 show stat while executing program


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
## pytr
```
usage: pytr [-h] match replacement

reads stdin and replaces chars with another chars

positional arguments:
  match        chars to find
  replacement  replacement chars

optional arguments:
  -h, --help   show this help message and exit

examples:
  echo %PATH% | pytr ";" "\n" | pygrep -i conda | pytr "\n" ";"
  echo %PATH% | pytr ";" "\n" | pygrep -i conda | pysed s,%USERPROFILE%,^%USERPROFILE^%,r | pytr "\n" ";"

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
usage: pywc [-h] [-l] [-w] [-m] [-c] [--input INPUT] [-X] [path ...]

calculates number or lines words, chars and bytes in files

positional arguments:
  path                  files

optional arguments:
  -h, --help            show this help message and exit
  -l                    print the newline counts
  -w                    print the word counts
  -m                    print the character counts
  -c                    print the byte counts
  --input INPUT, -i INPUT
                        read file paths from file
  -X, --xargs           read file paths from stdin

examples:
  pywc -l text.txt
  pyfind -iname *.txt | pywc -l --input-stdin

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
