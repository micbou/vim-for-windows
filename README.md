[![AppVeyor build status](https://ci.appveyor.com/api/projects/status/twwsyen7192tjq17/branch/master?svg=true)](https://ci.appveyor.com/project/micbou/vim-for-windows/branch/master)
[![Bintray download](https://api.bintray.com/packages/micbou/generic/vim/images/download.svg)](https://bintray.com/micbou/generic/vim/_latestVersion)

# Vim for Windows

Vim 32-bit and 64-bit releases for Windows including support for the following
interfaces:
 - [Lua 5.3](https://sourceforge.net/projects/luabinaries/files/);
 - [Perl 5.24](https://www.activestate.com/activeperl/downloads);
 - [Python 2.7](https://www.python.org/downloads/release/python-2713/);
 - [Python 3.6](https://www.python.org/downloads/release/python-362/);
 - [Racket 6.10](https://racket-lang.org/download/);
 - [Ruby 2.4](https://rubyinstaller.org/downloads/);
 - [Tcl 8.6](https://www.activestate.com/activetcl/downloads).

You need to download and install these softwares to use the corresponding
interfaces in Vim. Once installed, add their libraries to your `PATH` (except
for Python 2):
 - add Lua root folder to load `lua53.dll`;
 - add Perl `bin` folder to load `perl524.dll`;
 - add Python 3 root folder to load `python36.dll`;
 - add Ruby `bin` folder to load `msvcrt-ruby240.dll` on 32-bit or
   `x64-msvcrt-ruby240.dll` on 64-bit;
 - add Tcl `bin` folder to load `tcl86.dll`.

Terminal support is also available. You need to [download
winpty](https://github.com/rprichard/winpty) then put the files `winpty.dll` and
`winpty-agent.exe` from the folder `ia32\bin` or `x64\bin` (depending on Vim
architecture) in your `PATH` to use this feature.

## Why? There is already nightly official Vim binaries for Windows.

For multiple reasons:
 - the official Vim binaries are not tested. I am not going to install untested
   software and you shouldn't too;
 - some interfaces in the official Vim binaries are not up to date: Python 3.5
   while 3.6 is available, Racket 6.6 while 6.10 is available, Ruby 2.2 while
   2.4 is available. I am always trying to support the latest interfaces version
   in the binaries I am distributing;
 - no official 64-bit installer;
 - my releases are available on
   [Bintray](https://bintray.com/micbou/generic/vim) and announced on
   [Twitter](https://twitter.com/mic_bou) so downloading them is fast (faster
   than GitHub) and it's easy to know when there is a new release (just follow
   the Twitter account).
