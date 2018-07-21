[![AppVeyor build status](https://ci.appveyor.com/api/projects/status/twwsyen7192tjq17/branch/master?svg=true)](https://ci.appveyor.com/project/micbou/vim-for-windows/branch/master)
[![Bintray download](https://api.bintray.com/packages/micbou/generic/vim/images/download.svg)](https://bintray.com/micbou/generic/vim/_latestVersion)

# Vim for Windows

Vim 32-bit and 64-bit releases for Windows including support for the following
interfaces:
 - [Lua 5.3](https://sourceforge.net/projects/luabinaries/files/);
 - [Perl 5.26](https://downloads.activestate.com/ActivePerl/releases);
 - [Python 2.7](https://www.python.org/downloads/release/python-2715/);
 - [Python 3.6](https://www.python.org/downloads/release/python-366/);
 - [Racket 6.12](https://racket-lang.org/download/);
 - [Ruby 2.4](https://rubyinstaller.org/downloads/);
 - [Tcl 8.6](https://downloads.activestate.com/ActiveTcl/releases).

You need to download and install these softwares to use the corresponding
interfaces in Vim. Once installed, add their libraries to your `PATH` (except
for Python 2):
 - add Lua root folder to load `lua53.dll`;
 - add Perl `bin` folder to load `perl526.dll`;
 - add Python 3 root folder to load `python36.dll`;
 - add Racket `lib` folder to load `libracket3m_a3rum8.dll`;
 - add Ruby `bin` and `bin\ruby_builtin_dlls` folders to load
   `msvcrt-ruby240.dll` on 32-bit or `x64-msvcrt-ruby240.dll` on 64-bit;
 - add Tcl `bin` folder to load `tcl86t.dll`.

Terminal support is also available (see `:h terminal`).

## Why? There is already nightly official Vim binaries for Windows.

For multiple reasons:
 - 64-bit installer;
 - latest versions of the interfaces;
 - releases available on
   [Bintray](https://bintray.com/micbou/generic/vim) and announced on
   [Twitter](https://twitter.com/mic_bou) so downloading them is fast (faster
   than GitHub) and it's easy to know when there is a new release (just follow
   the Twitter account).
