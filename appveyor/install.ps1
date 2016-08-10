$script_path = split-path -parent $MyInvocation.MyCommand.Definition
. $script_path\utils.ps1

#
# Update submodule
#
Invoke-Expression "git submodule update --init"

#
# Install Lua
#

$lua_url = "http://sourceforge.net/projects/luabinaries/files/$env:lua_version/Windows%20Libraries/Dynamic/lua-$($env:lua_version)_Win$($env:arch)_dllw4_lib.zip/download"
$lua_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\lua.zip"
Invoke-Download $lua_url $lua_output
Invoke-Expression "& 7z x '$lua_output' -oC:\Lua" | out-null
$env:PATH = "C:\Lua;$env:PATH"

#
# Install Perl
#

If ($env:arch -eq 32) {
    $perl_arch = "x86-64int"
    $perl_revision = $env:perl32_revision
} Else {
    $perl_arch = "x64"
    $perl_revision = $env:perl64_revision
}
$perl_folder = "ActivePerl-$env:perl_version-MSWin32-$perl_arch-$perl_revision"
$perl_url = "http://downloads.activestate.com/ActivePerl/releases/$env:perl_version/$perl_folder.zip"
$perl_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$perl_folder.zip"
Invoke-Download $perl_url $perl_output
Invoke-Expression "& 7z x '$perl_output' -oC:\" | out-null

# Deduce minimal version format from full version (ex: 5.22.1.2201 gives 522).
$perl_version_array = $env:perl_version.Split('.')
$perl_minimal_version = $perl_version_array[0] + $perl_version_array[1]

Move-Item C:\$perl_folder C:\Perl$perl_minimal_version

$env:PATH = "C:\Perl$perl_minimal_version\perl\bin;$env:PATH"

#
# Install Racket
#

If ($env:arch -eq 32) {
    $racket_arch = "i386"
} Else {
    $racket_arch = "x86_64"
}
$racket_installer_name = "racket-minimal-$env:racket_version-$racket_arch-win32.exe"
$racket_url = "https://mirror.racket-lang.org/releases/$env:racket_version/installers/$racket_installer_name"
$racket_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$racket_installer_name"
Invoke-Download $racket_url $racket_output
Start-Process "$racket_output" -ArgumentList "/S /D=C:\Racket" -Wait

$env:PATH = "C:\Racket;$env:PATH"

#
# Install Ruby
#

# RubyInstaller is built with MinGW, so we cannot use header files from it.
# Download the source files and generate config.h for MSVC.

# Get the branch according to Ruby version.
$ruby_version_array = $env:ruby_version.Split('.')
$ruby_branch = "ruby_" + $ruby_version_array[0] + "_" + $ruby_version_array[1]
$ruby_minimal_version = $ruby_version_array[0] + $ruby_version_array[1]
$ruby_directory = "$env:APPVEYOR_BUILD_FOLDER\downloads\ruby"

Invoke-GitClone "https://github.com/ruby/ruby.git" $ruby_directory "$ruby_branch"
Push-Location -Path $ruby_directory

# Set Visual Studio environment variables.
$vc_vars_script_path = (Get-Item env:"VS$($env:msvc)0COMNTOOLS").Value + "..\..\VC\vcvarsall.bat"
If ($env:arch -eq 32) {
    $vc_vars_arch = "x86"
} Else {
    $vc_vars_arch = "x86_amd64"
}

$old_env = Get-Environment

Invoke-CmdScript $vc_vars_script_path $vc_vars_arch
Invoke-Expression "& win32\configure.bat"
Invoke-Expression "& nmake .config.h.time"

Restore-Environment $old_env

If ($env:arch -eq 32) {
    $ruby_include_folder = "i386-mswin32_$($env:msvc)0"
    $ruby_path = "C:\Ruby$ruby_minimal_version"
} Else {
    $ruby_include_folder = "x64-mswin64_$($env:msvc)0"
    $ruby_path = "C:\Ruby$ruby_minimal_version-x64"
}

Copy-Item .ext\include\$ruby_include_folder $ruby_path\include\ruby-$env:ruby_version -Recurse
Pop-Location

$env:PATH = "$ruby_path\bin;$env:PATH"

#
# Install Tcl
#

If ($env:arch -eq 32) {
    $tcl_arch = "ix86"
} Else {
    $tcl_arch = "x86_64"
}
$tcl_installer_name = "ActiveTcl$env:tcl_version.$env:tcl_revision-win32-$tcl_arch-threaded.exe"
$tcl_url = "http://downloads.activestate.com/ActiveTcl/releases/$env:tcl_version/$tcl_installer_name"
$tcl_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$tcl_installer_name"
Invoke-Download $tcl_url $tcl_output
Start-Process "$tcl_output" -ArgumentList "--directory C:\Tcl" -Wait

$env:PATH = "C:\Tcl\bin;$env:PATH"

#
# Get libintl.dll, iconv.dll, and possibly libwinpthread.dll.
#
$gettext_installer_name = "gettext0.19.6-iconv1.14-shared-64.exe"
$gettext_url = "https://github.com/mlocati/gettext-iconv-windows/releases/download/v0.19.6-v1.14/$gettext_installer_name"
$gettext_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$gettext_installer_name"
Invoke-Download $gettext_url $gettext_output
Start-Process "$gettext_output" -ArgumentList "/verysilent /dir=C:\gettext" -Wait
Copy-Item C:\gettext\libintl-8.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
Copy-Item C:\gettext\libiconv-2.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
# Copy libwinpthread only for 64-bit.
If ($env:arch -eq 64) {
    Copy-Item C:\gettext\libwinpthread-1.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
}

$env:PATH = "C:\gettext;$env:PATH"

#
# Add NSIS to PATH.
#

$env:PATH = "C:\Program Files (x86)\NSIS;$env:PATH"

#
# Install UPX.
#

$upx_archive_name = "upx391w.zip"
$upx_url = "http://upx.sourceforge.net/download/$upx_archive_name"
$upx_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$upx_archive_name"
Invoke-Download $upx_url $upx_output
Invoke-Expression "& 7z x '$upx_output' -oC:\" | out-null
$env:PATH = "C:\upx391w;$env:PATH"

#
# Download and install pip for Bintray script requirement.
#

$pip_installer_name = "get-pip.py"
$pip_url = "https://bootstrap.pypa.io/get-pip.py"
$pip_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$pip_installer_name"
Invoke-Download $pip_url $pip_output
Invoke-Expression "& python '$pip_output'"
Invoke-Expression "& C:\Python27\Scripts\pip install requests twitter"
