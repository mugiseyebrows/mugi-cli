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

options:
  -h, --help  show this help message and exit
  --text, -t

```
## pycol
```
usage: pycol [-h] [-n N [N ...]] [path ...]

extracts and prints specific columns

positional arguments:
  path

options:
  -h, --help    show this help message and exit
  -n N [N ...]  column number

```
## pycwd
```
usage: pycwd [-h]

prints current working directory

options:
  -h, --help  show this help message and exit

```
## pydos2unix
```
usage: pydos2unix [-h] [path ...]

converts line endings from dos to unix (\r\n -> \n)

positional arguments:
  path

options:
  -h, --help  show this help message and exit

```
## pydu
```
usage: [-s] [-f] [-d] [-h] [--help] [path ...]

positional arguments:
  path

options:
  -s      print summary only
  -f      print files stat
  -d      print directories stat
  -h      print in human friendly units (KB, MB, GB, TB)
  --help

examples:

```
## pyecho
```
usage: pyecho [-e] [-n] [--stdout] [args...] [--stderr] [args...]

prints text to stdout and stderr

options:
  -h --help  show this message and exit
  -e         decode escape sequences
  -n         do not print newline
  --stdout   print following args to stdout
  --stderr   print following args to stderr

examples:
  pyecho hello world
  pyecho -e "1\n2\n3"
  pyecho -n test
  pyecho {1..5}
  pyecho this goes to stdout --stderr this goes to stderr


```
## pyexec
```
usage: pyexec commands

executes one or more commands conditionally

options:
  -h, --help  show this help message and exit

examples:
  pyexec "echo 1 && echo 2 || echo 3 && echo 4; pytrue && echo 5; pyfalse && echo 6"
  pyexec "echo 'some file.txt'; pycat 'some file.txt'"
  pyexec pytrue "&&" echo {1..3}



```
## pyextstat
```
usage: pyextstat [-s] [--help] [-h] [-o {s,c,size,count}] [--skip-git] [-X]
                    [--maxdepth MAXDEPTH] [--sample SAMPLE]
                    [path ...]

prints file extension statistics

positional arguments:
  path                  paths

options:
  -s, --short           show short list
  --help                show help
  -h, --human-readable  human readable sizes
  -o {s,c,size,count}, --order {s,c,size,count}
                        sort order
  --skip-git
  -X, --xargs           read paths from stdin
  --maxdepth MAXDEPTH
  --sample SAMPLE

```
## pyfalse
```
usage: pyfalse [-h]

exits with code 1

options:
  -h, --help  show this help message and exit

```
## pyfor
```

usage: pyfor [-h] [--help] [-n COUNT] [--list items...] [--glob exprs...] [--sleep SECONDS] 
  [--at] [-v] [--sep-nl | --sep-sp] [--blank-line] [--] command [args]

optional arguments:
  -n COUNT               run command COUNT times
  --list items...        run command for each item in list
  --glob items...        run command for each path matched by globs
  -s, --sleep SECONDS    sleep SECONDS after command
  --at                   print current time and separator before executing command
  -v, --verbose          print command and separator before executing command
  --sep-nl               separator is newline
  --sep-sp               separator is space (default)
  --blank-line           print blank line after command output

examples:
  pyfor -n 5 echo hello world :iter:
  pyfor -n 10 -s 10 --blank-line pyexec tasklist "|" pygrep python
  pyfor -s 60 --at pynmap example.com -p 80
  pyfor -s 30 --blank-line pyfind build -mmin -0.1
  pyfor --list pytrue pyfalse -- pyexec :iter: "&&" echo yeah :iter: "||" echo meh :iter:

runs command(s) n times or forever


```
## pyfree
```
usage: pyfree [--help] [-h]

options:
  --help
  -h, -g, -G

```
## pygrep
```
usage: pygrep [-i] [-o] [-v] [-H] [-h] [-n] [--help] expr [path ...]

prints matching lines

positional arguments:
  expr
  path

options:
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
usage: pyhead [-h] [-n LINES] [-c BYTES] [-o OFFSET] [-q] [file ...]

outputs first n lines (or bytes) of file or stdin

positional arguments:
  file

options:
  -h, --help            show this help message and exit
  -n LINES, --lines LINES
                        number of lines
  -c BYTES, --bytes BYTES
                        number of bytes
  -o OFFSET, --offset OFFSET
  -q, --quiet           do not print header

```
## pyiconv
```
usage: pyiconv [-h] [-f FROM] [-t TO]

converts text from one encoding to another

options:
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

options:
  -h, --help  show this help message and exit

```
## pymd5sum
```
usage: pymd5sum [-h] [path ...]

prints md5 hashsum of file

positional arguments:
  path

options:
  -h, --help  show this help message and exit

```
## pymtime
```
usage: pymtime [-h] [path ...]

prints mtime of file

positional arguments:
  path

options:
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

options:
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
## pynmap
```
usage: [-h] [-p PORTS [PORTS ...]] [-t TIMEOUT] [-v] [-s] hosts [hosts ...]

positional arguments:
  hosts                 hosts to scan

options:
  -h, --help            show this help message and exit
  -p PORTS [PORTS ...], --ports PORTS [PORTS ...]
                        ports to scan
  -t TIMEOUT, --timeout TIMEOUT
                        timeout for connection
  -v, --verbose         show errors
  -s, --short           short output (print only open ports)

examples:
  pynmap 192.168.0.1-100 -p 80,8080
  pynmap 192.168.0.1/24 -p 1000-2000
  pynmap google.com -p 80

```
## pynth
```
usage: pynth [-h] [-n N] [path ...]

positional arguments:
  path

options:
  -h, --help  show this help message and exit
  -n N

```
## pyplot
```
usage: pyplot [-h] [path ...]

plots data

positional arguments:
  path

options:
  -h, --help  show this help message and exit

```
## pyprintcmd
```
usage: pyprintcmd [--help] args...
prints args to stdout as python array


```
## pyrandom
```
usage: pyrandom [-h] [-w] [-l LENGTH LENGTH] [-n NUMBER] [-s]

options:
  -h, --help            show this help message and exit
  -w, --words
  -l LENGTH LENGTH, --length LENGTH LENGTH
  -n NUMBER, --number NUMBER
  -s, --space

```
## pysed
```
usage: pysed [-h] [-e E] expr [path ...]

replaces text according to expressions

positional arguments:
  expr
  path

options:
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

options:
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

options:
  -h, --help  show this help message and exit

```
## pysha224sum
```
usage: pysha224sum [-h] [path ...]

prints sha224 hashsum of file

positional arguments:
  path

options:
  -h, --help  show this help message and exit

```
## pysha256sum
```
usage: pysha256sum [-h] [path ...]

prints sha256 hashsum of file

positional arguments:
  path

options:
  -h, --help  show this help message and exit

```
## pysha384sum
```
usage: pysha384sum [-h] [path ...]

prints sha384 hashsum of file

positional arguments:
  path

options:
  -h, --help  show this help message and exit

```
## pysha512sum
```
usage: pysha512sum [-h] [path ...]

prints sha512 hashsum of file

positional arguments:
  path

options:
  -h, --help  show this help message and exit

```
## pysleep
```
usage: pysleep [-h] [-p PRINT] time [time ...]

sleeps for TIME seconds

positional arguments:
  time

options:
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

options:
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

options:
  -h, --help  show this help message and exit
  --show

```
## pytail
```
usage: pytail [-h] [-n LINES] [-c BYTES] [-q] [file ...]

outputs last n lines (or bytes) of file or stdin

positional arguments:
  file

options:
  -h, --help            show this help message and exit
  -n LINES, --lines LINES
                        number of lines
  -c BYTES, --bytes BYTES
                        number of bytes
  -q, --quiet           do not print header

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

options:
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

options:
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

options:
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

options:
  -h, --help            show this help message and exit
  -L LEVEL, --level LEVEL
                        depth
  -i INCLUDE [INCLUDE ...], --include INCLUDE [INCLUDE ...]
                        include files globs
  -e EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                        include files globs

```
## pytrue
```

```
## pyuniq
```
usage: pyuniq [-h] [--count] [--repeated] [--unique] [path ...]

prints unique or nonunique lines from sorted array of lines

positional arguments:
  path

options:
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

options:
  -h, --help  show this help message and exit

```
## pyuptime
```
usage: pyuptime [-h] [-p]

prints uptime information

options:
  -h, --help    show this help message and exit
  -p, --pretty  pretty print

```
## pywc
```
usage: pywc [-h] [-l] [-w] [-m] [-c] [--input INPUT] [-X] [path ...]

calculates number or lines words, chars and bytes in files

positional arguments:
  path                  files

options:
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

options:
  -h, --help            show this help message and exit
  -s SEEK, --seek SEEK  start at offset
  -l LEN, --len LEN     number of bytes to print

```
## pyzip
```
usage: pyzip [-h] [--type {d,f}] [--depth DEPTH] [--strip STRIP]
                [--prepend PREPEND] [--include INCLUDE [INCLUDE ...]]
                [--exclude EXCLUDE [EXCLUDE ...]] [--list LIST] [--stdin]
                [-o OUTPUT] [-m {deflate,d,lzma,l,bzip2,b,store,s}] [-l L]
                [--base BASE] [-s] [-v]
                {a,x,l} zip [sources ...]

appends, extracts and list contents of zip archive

positional arguments:
  {a,x,l}               add extract list
  zip
  sources

options:
  -h, --help            show this help message and exit
  --type {d,f}          list only files or only dirs
  --depth DEPTH         list depth
  --strip STRIP         strip n path components
  --prepend PREPEND     prepend to path
  --include INCLUDE [INCLUDE ...], -i INCLUDE [INCLUDE ...]
                        paths or globs to exclude
  --exclude EXCLUDE [EXCLUDE ...], -e EXCLUDE [EXCLUDE ...]
                        paths or globs to include
  --list LIST           path to list of files
  --stdin               read paths from stdin
  -o OUTPUT, --output OUTPUT
                        output directory
  -m {deflate,d,lzma,l,bzip2,b,store,s}
                        compression method
  -l L                  compression level 0..9 for deflate (0 - best speed, 9
                        - best compression) 1..9 for bzip2, has no effect if
                        method is store or lzma
  --base BASE           base directory
  -s, --silent
  -v, --verbose

```
# Notes

Windows shell (cmd) doesn't expand wildcards so you dont need to put them in quotes, also you dont need to escape parenthesis and semicolon. Escape symbol for special chars is ^, not \

/dev/null windows alternative is NUL

# See also

[https://github.com/mugiseyebrows/pyfindlib](https://github.com/mugiseyebrows/pyfindlib)


