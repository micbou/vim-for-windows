$script_path = split-path -parent $MyInvocation.MyCommand.Definition
. $script_path\utils.ps1

#
# Get libintl and libiconv for both architectures.
#

ForEach ($gettext_arch In 32, 64) {
    $gettext_installer_name = "gettext0.19.8.1-iconv1.14-shared-$gettext_arch.exe"
    $gettext_url = "https://github.com/mlocati/gettext-iconv-windows/releases/download/v0.19.8.1-v1.14/$gettext_installer_name"
    $gettext_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$gettext_installer_name"
    Invoke-Download $gettext_url $gettext_output
    $gettext_dir = "C:\gettext$gettext_arch"
    Start-Process "$gettext_output" -ArgumentList "/verysilent /dir=$gettext_dir" -Wait
    $runtime_dir = "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
    $gvimext_dir = "$runtime_dir\GvimExt$gettext_arch"
    New-Item $gvimext_dir -type directory
    $gettext_runtime_dir = "$runtime_dir\gettext$gettext_arch"
    New-Item $gettext_runtime_dir -type directory
    Copy-Item $gettext_dir\bin\libintl-8.dll $gvimext_dir
    Copy-Item $gettext_dir\bin\libintl-8.dll $gettext_runtime_dir
    Copy-Item $gettext_dir\bin\libiconv-2.dll $gvimext_dir
    Copy-Item $gettext_dir\bin\libiconv-2.dll $gettext_runtime_dir
    If (Test-Path $gettext_dir\bin\libgcc_s_sjlj-1.dll) {
        Copy-Item $gettext_dir\bin\libgcc_s_sjlj-1.dll $gvimext_dir
        Copy-Item $gettext_dir\bin\libgcc_s_sjlj-1.dll $gettext_runtime_dir
    }
}
$gettext_dir = "C:\gettext$env:arch"
$runtime_dir = "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
Copy-Item $gettext_dir\bin\libintl-8.dll $runtime_dir
Copy-Item $gettext_dir\bin\libiconv-2.dll $runtime_dir
If (Test-Path $gettext_dir\bin\libgcc_s_sjlj-1.dll) {
    Copy-Item $gettext_dir\bin\libgcc_s_sjlj-1.dll $runtime_dir
}
