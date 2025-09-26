param(
    [string]$Comfy = "$HOME\ComfyUI"
)
$Here = (Split-Path -Parent $MyInvocation.MyCommand.Path) | Split-Path -Parent
$Target = Join-Path $Comfy "custom_nodes\comfyui-xdev-nodes"
New-Item -ItemType Directory -Force -Path (Split-Path $Target) | Out-Null
if (Test-Path $Target) { Remove-Item $Target -Force }
cmd /c mklink /D "$Target" "$Here" | Out-Null
Write-Host "Linked $Here -> $Target"
