# Invokes a Cmd.exe shell script and updates the environment.
function Invoke-CmdScript {
    param(
            [String] $scriptName
         )
    $cmdLine = """$scriptName"" $args & set"
    & $Env:SystemRoot\system32\cmd.exe /c $cmdLine |
    Select-String '^([^=]*)=(.*)$' | Foreach-Object {
        $varName = $_.Matches[0].Groups[1].Value
            $varValue = $_.Matches[0].Groups[2].Value
            Set-Item Env:$varName $varValue
    }
}

# Returns the current environment.
function Get-Environment {
    Get-Childitem Env:
}

# Restores the environment to a previous state.
function Restore-Environment {
    param(
            [parameter(Mandatory=$TRUE)]
            [System.Collections.DictionaryEntry[]] $oldEnv
         )
    # Remove any added variables.
    Compare-Object $oldEnv $(Get-Environment) -property Key -passthru |
    Where-Object { $_.SideIndicator -eq "=>" } |
    Foreach-Object { Remove-Item Env:$($_.Name) }
    # Revert any changed variables to original values.
    Compare-Object $oldEnv $(Get-Environment) -property Value -passthru |
    Where-Object { $_.SideIndicator -eq "<=" } |
    Foreach-Object { Set-Item Env:$($_.Name) $_.Value }
}
