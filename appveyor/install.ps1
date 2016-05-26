$script_path = split-path -parent $MyInvocation.MyCommand.Definition
. $script_path\environment.ps1

#
# Update submodule
#
Invoke-Expression "git submodule update --init"

#
# Install Lua
#

$lua_url = "http://sourceforge.net/projects/luabinaries/files/$env:lua_version/Windows%20Libraries/Dynamic/lua-$($env:lua_version)_Win$($env:arch)_dllw4_lib.zip/download"
$lua_output = "$env:APPVEYOR_BUILD_FOLDER\lua.zip"
(New-Object System.Net.WebClient).DownloadFile($lua_url, $lua_output)
Invoke-Expression "& 7z x '$lua_output' -oC:\Lua" | out-null
$env:PATH = "C:\Lua;$env:PATH"

#
# Install Perl
#

if ($env:arch -eq 32) {
    $perl_arch = "x86-64int"
} else {
    $perl_arch = "x64"
}
$perl_folder = "ActivePerl-$env:perl_version-MSWin32-$perl_arch-$env:perl_revision"
$perl_url = "http://downloads.activestate.com/ActivePerl/releases/$env:perl_version/$perl_folder.zip"
$perl_output = "$env:APPVEYOR_BUILD_FOLDER\$perl_folder.zip"
(New-Object System.Net.WebClient).DownloadFile($perl_url, $perl_output)
Invoke-Expression "& 7z x '$perl_output' -oC:\" | out-null

# Deduce minimal version format from full version (ex: 5.22.1.2201 gives 522).
$perl_version_array = $env:perl_version.Split('.')
$perl_minimal_version = $perl_version_array[0] + $perl_version_array[1]

Move-Item C:\$perl_folder C:\Perl$perl_minimal_version

$env:PATH = "C:\Perl$perl_minimal_version\perl\bin;$env:PATH"

#
# Install Racket
#

if ($env:arch -eq 32) {
    $racket_arch = "i386"
} else {
    $racket_arch = "x86_64"
}
$racket_installer_name = "racket-minimal-$env:racket_version-$racket_arch-win32.exe"
$racket_url = "https://mirror.racket-lang.org/releases/$env:racket_version/installers/$racket_installer_name"
$racket_output = "$env:APPVEYOR_BUILD_FOLDER\$racket_installer_name"
(New-Object System.Net.WebClient).DownloadFile($racket_url, $racket_output)
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

Invoke-Expression "git clone https://github.com/ruby/ruby.git -b $ruby_branch --depth 1 -q $env:APPVEYOR_BUILD_FOLDER\ruby"
Push-Location -Path "$env:APPVEYOR_BUILD_FOLDER\ruby"

# Set Visual Studio environment variables.
$vc_vars_script_path = (Get-Item env:"VS$($env:msvc)0COMNTOOLS").Value + "..\..\VC\vcvarsall.bat"
if ($env:arch -eq 32) {
    $vc_vars_arch = "x86"
} else {
    $vc_vars_arch = "x86_amd64"
}

$old_env = Get-Environment

Invoke-CmdScript $vc_vars_script_path $vc_vars_arch
Invoke-Expression "& win32\configure.bat"
Invoke-Expression "& nmake .config.h.time"

Restore-Environment $old_env

if ($env:arch -eq 32) {
    $ruby_include_folder = "i386-mswin32_$($env:msvc)0"
    $ruby_path = "C:\Ruby$ruby_minimal_version"
} else {
    $ruby_include_folder = "x64-mswin64_$($env:msvc)0"
    $ruby_path = "C:\Ruby$ruby_minimal_version-x64"
}

Copy-Item .ext\include\$ruby_include_folder $ruby_path\include\ruby-$env:ruby_version -Recurse
Pop-Location

$env:PATH = "$ruby_path\bin;$env:PATH"

#
# Install Tcl
#

if ($env:arch -eq 32) {
    $tcl_arch = "ix86"
} else {
    $tcl_arch = "x86_64"
}
$tcl_installer_name = "ActiveTcl$env:tcl_version.$env:tcl_revision-win32-$tcl_arch-threaded.exe"
$tcl_url = "http://downloads.activestate.com/ActiveTcl/releases/$env:tcl_version/$tcl_installer_name"
$tcl_output = "$env:APPVEYOR_BUILD_FOLDER\$tcl_installer_name"
(New-Object System.Net.WebClient).DownloadFile($tcl_url, $tcl_output)
Start-Process "$tcl_installer_name" -ArgumentList "--directory C:\Tcl" -Wait

$env:PATH = "C:\Tcl\bin;$env:PATH"

#
# Get libintl.dll, iconv.dll, and possibly libwinpthread.dll.
#
$gettext_installer_name = "gettext0.19.6-iconv1.14-shared-64.exe"
$gettext_url = "https://github.com/mlocati/gettext-iconv-windows/releases/download/v0.19.6-v1.14/$gettext_installer_name"
$gettext_output = "$env:APPVEYOR_BUILD_FOLDER\$gettext_installer_name"
(New-Object System.Net.WebClient).DownloadFile($gettext_url, $gettext_output)
Start-Process "$gettext_output" -ArgumentList "/verysilent /dir=C:\gettext" -Wait
Copy-Item C:\gettext\libintl-8.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
Copy-Item C:\gettext\libiconv-2.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
# Copy libwinpthread only for 64-bit.
if ($env:arch -eq 64) {
    Copy-Item C:\gettext\libwinpthread-1.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
}

$env:PATH = "C:\gettext;$env:PATH"

#
# Install NSIS
#

$nsis_installer_name = "nsis-3.0rc1-setup.exe"
$nsis_url = "http://prdownloads.sourceforge.net/nsis/$nsis_installer_name"
$nsis_output = "$env:APPVEYOR_BUILD_FOLDER\$nsis_installer_name"
(New-Object System.Net.WebClient).DownloadFile($nsis_url, $nsis_output)
Start-Process "$nsis_output" -ArgumentList "/S /D=C:\NSIS"
$env:PATH = "C:\NSIS;$env:PATH"

#
# Install UPX.
#

$upx_archive_name = "upx391w.zip"
$upx_url = "http://upx.sourceforge.net/download/$upx_archive_name"
$upx_output = "$env:APPVEYOR_BUILD_FOLDER\$upx_archive_name"
(New-Object System.Net.WebClient).DownloadFile($upx_url, $upx_output)
Invoke-Expression "& 7z x '$upx_output' -oC:\" | out-null
$env:PATH = "C:\upx391w;$env:PATH"

#
# Download and install pip for Bintray script requirement.
#

$pip_installer_name = "get-pip.py"
$pip_url = "https://bootstrap.pypa.io/get-pip.py"
$pip_output = "$env:APPVEYOR_BUILD_FOLDER\$pip_installer_name"
(New-Object System.Net.WebClient).DownloadFile($pip_url, $pip_output)
Invoke-Expression "& python '$pip_output'"
Invoke-Expression "& C:\Python27\Scripts\pip install requests twitter"

# Fix test86 failure introduced by python 2.7.11
# TODO: check if this is still needed when python 2.7.12 is released.
Invoke-Expression "& C:\Windows\System32\reg copy HKLM\SOFTWARE\Python\PythonCore\2.7 HKLM\SOFTWARE\Python\PythonCore\2.7-32 /s /reg:32"
Invoke-Expression "& C:\Windows\System32\reg copy HKLM\SOFTWARE\Python\PythonCore\2.7 HKLM\SOFTWARE\Python\PythonCore\2.7-32 /s /reg:64"
