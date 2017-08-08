# Input environment variables:
#   arch: Architecture (32 or 64)
#   msvc: Microsoft Visual C++ version (11, 12, 14)
#   appveyor_repo_tag_name: AppVeyor tag (Vim tags are in vX.Y.Z form)
#   lua_version: Lua version
#   perl_version: Perl version
#   python2_version: Python 2 version
#   python3_version: Python 3 version
#   racket_version: Racket version
#   ruby_version: Ruby version
#   tcl_version: Tcl version
#   bintray_username: Bintray username
#
# Output environment variables:
#   vim_version: Vim version in X.Y.Z form
#   vim_artifact: Vim executable name
#   vim_tweet: message send on Twitter
#   git_description: release notes on GitHub
#   bintray_description: description on Bintray

Function GetMajorMinorVersion($version) {
    $version_array = $version.Split('.')
    $version_array[0] + '.' + $version_array[1]
}

$vim_version = $env:appveyor_repo_tag_name.Substring(1)

If ($env:arch -eq 32) {
    $vim_arch = "x86"
} Else {
    $vim_arch = "x64"
}

$msvc = $env:appveyor_build_worker_image.Substring(14)
If ($msvc -eq 2013) {
    $env:msvc = 12
} ElseIf ($msvc -eq 2015) {
    $env:msvc = 14
} ElseIf ($msvc -eq 2017) {
    $env:msvc = 15
}

$vim_executable_name = "vim$vim_version-$vim_arch.exe"

$lua_major_minor_version = GetMajorMinorVersion $env:lua_version
$perl_major_minor_version = GetMajorMinorVersion $env:perl_version
$python2_major_minor_version = GetMajorMinorVersion $env:python2_version
$python3_major_minor_version = GetMajorMinorVersion $env:python3_version
$racket_major_minor_version = GetMajorMinorVersion $env:racket_version
$ruby_major_minor_version = GetMajorMinorVersion $env:ruby_version
$tcl_major_minor_version = GetMajorMinorVersion $env:tcl_version

$logs = (git show -s --pretty=format:%b $env:appveyor_repo_tag_name) | Out-String
# AppVeyor uses "\n" as a convention for newlines in GitHub description
$git_description = $logs.Replace("`r`n", "\n")

$env:vim_version = $vim_version
$env:vim_artifact = $vim_executable_name
$env:vim_tweet = "Vim $vim_version $env:arch-bit for Windows released: https://bintray.com/artifact/download/$env:bintray_username/generic/$vim_executable_name"
$env:bintray_description = "Vim $vim_version 32-bit and 64-bit for Windows with Lua $lua_major_minor_version, Perl $perl_major_minor_version, Python $python2_major_minor_version, Python $python3_major_minor_version, Racket $racket_major_minor_version, Ruby $ruby_major_minor_version, and Tcl $tcl_major_minor_version support. Compiled with MSVC $env:msvc."
$env:git_description = $git_description
