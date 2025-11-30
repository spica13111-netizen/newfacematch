<#
claude_bash_setup.ps1
Detects Git Bash on Windows and optionally sets the CLAUDE_CODE_GIT_BASH_PATH environment variable.

Usage examples:
  # Just scan and show findings
  pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\claude_bash_setup.ps1

  # Automatically set for current user (recommended)
  pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\claude_bash_setup.ps1 -AutoSet -Scope User

  # Set system-wide (requires admin)
  pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\claude_bash_setup.ps1 -AutoSet -Scope Machine
#>
param(
    [switch] $AutoSet,
    [ValidateSet('User','Machine')]
    [string] $Scope = 'User',
    [switch] $VerboseOutput
)

function Write-Log($text, $level='INFO') {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Write-Host "[$ts] [$level] $text"
}

function Find-BashPath {
    $candidates = @()

    # 1) Check Get-Command / where
    try {
        $cmd = Get-Command bash.exe -ErrorAction SilentlyContinue
        if ($cmd) { $candidates += $cmd.Source }
    } catch { }

    try {
        $where = & where.exe bash 2>$null
        if ($where) { $candidates += $where }
    } catch { }

    # 2) Common installation paths
    $commonPaths = @(
        'C:\Program Files\Git\bin\bash.exe',
        'C:\Program Files\Git\usr\bin\bash.exe',
        'C:\Program Files (x86)\Git\bin\bash.exe',
        "$env:ProgramFiles\Git\bin\bash.exe",
        "$env:ProgramFiles\Git\usr\bin\bash.exe",
        "$env:ProgramFiles(x86)\Git\bin\bash.exe"
    )
    foreach ($p in $commonPaths) { if (Test-Path $p) { $candidates += $p } }

    # 3) Check registry uninstall entries for Git for Windows
    try {
        $uninstallPaths = @(
            'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
            'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
            'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
        )
        foreach ($u in $uninstallPaths) {
            Get-ChildItem -Path $u -ErrorAction SilentlyContinue | ForEach-Object {
                $displayName = (Get-ItemProperty -Path $_.PSPath -Name DisplayName -ErrorAction SilentlyContinue).DisplayName
                if ($displayName -and $displayName -match 'Git') {
                    $installLocation = (Get-ItemProperty -Path $_.PSPath -Name InstallLocation -ErrorAction SilentlyContinue).InstallLocation
                    if ($installLocation) {
                        $testPath1 = Join-Path $installLocation 'bin\bash.exe'
                        $testPath2 = Join-Path $installLocation 'usr\bin\bash.exe'
                        if (Test-Path $testPath1) { $candidates += $testPath1 }
                        if (Test-Path $testPath2) { $candidates += $testPath2 }
                    }
                }
            }
        }
    } catch { }

    # Make unique and return full paths
    $candidates | Select-Object -Unique
}

# --- main ---
Write-Log 'Starting Git Bash detection for CLAUDE_CODE_GIT_BASH_PATH'

$found = Find-BashPath
if (-not $found) {
    Write-Log 'No bash.exe found on this machine using common checks.' 'WARN'
    Write-Host "\nTips:"
    Write-Host " - Install Git for Windows: https://git-scm.com/downloads/win"
    Write-Host " - After installing, re-run this script to auto-detect bash.exe."
    exit 2
}

Write-Log "Found the following bash.exe candidates:`n$($found -join "`n")"

# Pick best candidate heuristically (prefer Program Files path)
$preferred = $found | Where-Object { $_ -match 'Program Files' } | Select-Object -First 1
if (-not $preferred) { $preferred = $found | Select-Object -First 1 }

Write-Log "Preferred bash path: $preferred"

# Show current environment variables
$currentSession = $env:CLAUDE_CODE_GIT_BASH_PATH
$userVar = [Environment]::GetEnvironmentVariable('CLAUDE_CODE_GIT_BASH_PATH','User')
$machineVar = [Environment]::GetEnvironmentVariable('CLAUDE_CODE_GIT_BASH_PATH','Machine')

Write-Host "`nCurrent session CLAUDE_CODE_GIT_BASH_PATH: $($currentSession -ne $null ? $currentSession : '<not set>')"
Write-Host "User-level CLAUDE_CODE_GIT_BASH_PATH: $($userVar -ne $null ? $userVar : '<not set>')"
Write-Host "Machine-level CLAUDE_CODE_GIT_BASH_PATH: $($machineVar -ne $null ? $machineVar : '<not set>')"

if ($AutoSet) {
    Write-Log "AutoSet enabled. Setting env var for scope: $Scope"
    try {
        # Validate required admin permission for Machine scope
        if ($Scope -eq 'Machine') {
            if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
                Write-Log 'Setting Machine-level variable requires elevated/admin rights. Please run PowerShell as Administrator.' 'ERROR'
                exit 3
            }
        }

        [Environment]::SetEnvironmentVariable('CLAUDE_CODE_GIT_BASH_PATH',$preferred,$Scope)
        Write-Log "Set CLAUDE_CODE_GIT_BASH_PATH to $preferred at $Scope scope" 'SUCCESS'

        # Inform user about restart requirement
        Write-Host "\nDone. Important: Any running apps (VS Code, terminals, services) need to be restarted to pick up the new environment variable."
        Write-Host "If you set Machine-level and restarted, you can re-open your Terminal/VSCode and run: `echo $env:CLAUDE_CODE_GIT_BASH_PATH` to verify it prints the path."

        exit 0
    } catch {
        Write-Log "Failed to set environment variable: $_" 'ERROR'
        exit 4
    }
} else {
    Write-Host "\nIf you want the script to set the variable for you automatically, re-run with -AutoSet -Scope User (or -Scope Machine as admin)."
    Write-Host "Example (user scope):\n  pwsh -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\claude_bash_setup.ps1 -AutoSet -Scope User"
    Write-Host "\nGUI steps (Control Panel -> System -> Advanced -> Environment Variables): Add a new USER variable named CLAUDE_CODE_GIT_BASH_PATH pointing to the preferred path shown above. Then restart VS Code/your terminal."
    exit 0
}
