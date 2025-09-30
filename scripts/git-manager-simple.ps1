# Git Manager for ComfyUI XDev Nodes
param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("status", "commit", "sync", "help")]
    [string]$Action,
    
    [Parameter(Position = 1)]
    [string]$Message = ""
)

function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "⚠️ $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ️ $msg" -ForegroundColor Cyan }

if (-not (Test-Path ".git")) {
    Write-Error "Not a git repository"
    exit 1
}

switch ($Action) {
    "status" {
        Write-Info "Git Status for XDev Nodes"
        
        $branch = git rev-parse --abbrev-ref HEAD 2>$null
        Write-Info "Current branch: $branch"
        
        $status = git status --porcelain 2>$null
        if ($status) {
            Write-Warning "Working directory has changes:"
            $status | ForEach-Object {
                $statusCode = $_.Substring(0, 2).Trim()
                $file = $_.Substring(3)
                
                if ($statusCode -eq "M") {
                    Write-Host "  📝 Modified: $file" -ForegroundColor Yellow
                } elseif ($statusCode -eq "A") {
                    Write-Host "  ➕ Added: $file" -ForegroundColor Green  
                } elseif ($statusCode -eq "D") {
                    Write-Host "  ➖ Deleted: $file" -ForegroundColor Red
                } elseif ($statusCode -eq "??") {
                    Write-Host "  ❓ Untracked: $file" -ForegroundColor Gray
                } else {
                    Write-Host "  🔄 $statusCode $file" -ForegroundColor White
                }
            }
        } else {
            Write-Success "Working directory is clean"
        }
        
        Write-Host ""
        Write-Info "Recent commits:"
        git log --oneline -5 2>$null | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    }
    
    "commit" {
        if (-not $Message) {
            Write-Error "Commit message required"
            exit 1
        }
        
        Write-Info "Creating commit for XDev Nodes..."
        git add .
        
        $commitMsg = "XDev v0.6.0-advanced: $Message"
        git commit -m $commitMsg
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Commit created successfully"
        } else {
            Write-Error "Commit failed"
        }
    }
    
    "sync" {
        Write-Info "Syncing with remote..."
        git pull
        git push
        Write-Success "Sync completed"
    }
    
    "help" {
        Write-Host ""
        Write-Info "Git Manager Commands:"
        Write-Host "  status  - Show repository status"
        Write-Host "  commit  - Create commit with message"  
        Write-Host "  sync    - Pull and push changes"
        Write-Host "  help    - Show this help"
        Write-Host ""
    }
}