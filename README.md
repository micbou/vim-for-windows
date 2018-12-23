[![AppVeyor build status](https://ci.appveyor.com/api/projects/status/twwsyen7192tjq17/branch/master?svg=true)](https://ci.appveyor.com/project/micbou/vim-for-windows/branch/master)
[![Bintray download](https://api.bintray.com/packages/micbou/generic/vim/images/download.svg)](https://bintray.com/micbou/generic/vim/_latestVersion)

**IMPORTANT:** this project is abandoned since [an official daily updated 64-bit
installer for Vim is
available](https://github.com/vim/vim-win32-installer/releases).

# Vim for Windows

Vim 32-bit and 64-bit releases for Windows including support for the following
interfaces:
 - [Lua 5.3](https://sourceforge.net/projects/luabinaries/files/);
 - [Perl 5.26](https://downloads.activestate.com/ActivePerl/releases);
 - [Python 2.7](https://www.python.org/downloads/release/python-2715/);
 - [Python 3.7](https://www.python.org/downloads/release/python-370/);
 - [Racket 7.0](https://racket-lang.org/download/);
 - [Ruby 2.5](https://rubyinstaller.org/downloads/);
 - [Tcl 8.6](https://downloads.activestate.com/ActiveTcl/releases).

You need to download and install these softwares to use the corresponding
interfaces in Vim. Once installed, add their libraries to your `PATH` (except
for Python 2):
 - add Lua root folder to load `lua53.dll`;
 - add Perl `bin` folder to load `perl526.dll`;
 - add Python 3 root folder to load `python37.dll`;
 - add Racket `lib` folder to load `libracket3m_bkrfgg.dll`;
 - add Ruby `bin` folder to load `msvcrt-ruby250.dll` on 32-bit or
   `x64-msvcrt-ruby250.dll` on 64-bit;
 - add Tcl `bin` folder to load `tcl86t.dll`.

Terminal support is also available (see `:h terminal`).
