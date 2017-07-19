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
Retry-Command -Command 'Invoke-Download' -Args @{ Url = $lua_url; Filepath = $lua_output }
Invoke-Expression "& 7z x '$lua_output' -oC:\Lua" | out-null
$env:PATH = "C:\Lua;$env:PATH"

#
# Install Perl
#

If ($env:arch -eq 32) {
    $perl_arch = "x86-64int"
    $perl_revision = $env:perl32_revision
    $perl_folder = "C:\Perl"
} Else {
    $perl_arch = "x64"
    $perl_revision = $env:perl64_revision
    $perl_folder = "C:\Perl64"
}
$perl_installer_name = "ActivePerl-$env:perl_version-MSWin32-$perl_arch-$perl_revision.exe"
$perl_url = "http://downloads.activestate.com/ActivePerl/releases/$env:perl_version/$perl_installer_name"
$perl_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$perl_installer_name"
Invoke-Download $perl_url $perl_output
Start-Process "$perl_output" -ArgumentList "/qn" -Wait
$env:PATH = "$perl_folder\bin;$env:PATH"

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

$paths = Get-ChildItem -Path "C:\Racket\lib"
foreach ($path in $paths)
{
    if ($path.Name -match "libracket(?<racket_library_version>[a-z0-9_]+)\.dll")
    {
        $env:racket_library_version = $matches['racket_library_version']
        break
    }
}

Write-Output "Racket library version: $env:racket_library_version"
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
# Get libintl and libiconv.
#

$gettext_installer_name = "gettext0.19.8.1-iconv1.14-shared-$env:arch.exe"
$gettext_url = "https://github.com/mlocati/gettext-iconv-windows/releases/download/v0.19.8.1-v1.14/$gettext_installer_name"
$gettext_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$gettext_installer_name"
Invoke-Download $gettext_url $gettext_output
Start-Process "$gettext_output" -ArgumentList "/verysilent /dir=C:\gettext" -Wait
Copy-Item C:\gettext\bin\libintl-8.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
Copy-Item C:\gettext\bin\libiconv-2.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
If (Test-Path C:\gettext\bin\libgcc_s_sjlj-1.dll) {
    Copy-Item C:\gettext\bin\libgcc_s_sjlj-1.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
}

$env:PATH = "C:\gettext\bin;$env:PATH"

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

#
# Install winpty.
#
If ($env:arch -eq 32) {
    $winpty_arch = "ia32"
} Else {
    $winpty_arch = "x64"
}
$winpty_archive_name = "winpty-0.4.3-msvc2015.zip"
$winpty_url = "https://github.com/rprichard/winpty/releases/download/0.4.3/$winpty_archive_name"
$winpty_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$winpty_archive_name"
Invoke-Download $winpty_url $winpty_output
Invoke-Expression "& 7z x '$winpty_output' -oC:\winpty" | out-null
Get-ChildItem "C:\winpty\$winpty_arch\bin"
$env:PATH = "C:\winpty\$winpty_arch\bin;$env:PATH"
Write-Host $env:PATH
