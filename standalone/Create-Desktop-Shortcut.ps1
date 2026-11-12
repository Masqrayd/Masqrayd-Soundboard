# Run after extracting the ZIP to a permanent folder.
# Creates a Desktop shortcut to the EXE in this folder; no installer required.
$ErrorActionPreference = 'Stop'
$exe = Join-Path $PSScriptRoot 'Masqrayd-Soundboard.exe'
if (-not (Test-Path $exe)) { throw "Masqrayd-Soundboard.exe not found beside this script." }
$desktop = [Environment]::GetFolderPath('Desktop')
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut((Join-Path $desktop 'Masqrayd Soundboard.lnk'))
$shortcut.TargetPath = $exe
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.Description = 'Masqrayd Soundboard - standalone Windows app'
$shortcut.IconLocation = "$exe,0"
$shortcut.Save()
Write-Host "Desktop shortcut created. Right-click the running app on the taskbar to pin it."
