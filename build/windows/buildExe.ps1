Write-Host "listing contents of C drive root"
Get-ChildItem -Path C:\ -Force

Write-Host "listing contents of cwd"
Get-ChildItem -Force
