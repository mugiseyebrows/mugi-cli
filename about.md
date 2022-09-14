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

