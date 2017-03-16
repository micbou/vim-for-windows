$script_path = split-path -parent $MyInvocation.MyCommand.Definition
. $script_path\utils.ps1

#
# Get libintl.dll and libiconv.dll.
#
$gettext_installer_name = "gettext0.19.8.1-iconv1.14-shared-64.exe"
$gettext_url = "https://github.com/mlocati/gettext-iconv-windows/releases/download/v0.19.8.1-v1.14/$gettext_installer_name"
$gettext_output = "$env:APPVEYOR_BUILD_FOLDER\downloads\$gettext_installer_name"
Invoke-Download $gettext_url $gettext_output
Start-Process "$gettext_output" -ArgumentList "/verysilent /dir=C:\gettext" -Wait
Copy-Item C:\gettext\bin\libintl-8.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
Copy-Item C:\gettext\bin\libiconv-2.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
If (Test-Path C:\gettext\bin\libgcc_s_sjlj-1.dll) {
    Copy-Item C:\gettext\bin\libgcc_s_sjlj-1.dll "$env:APPVEYOR_BUILD_FOLDER\vim\runtime"
}
