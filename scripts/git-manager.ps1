# Git Manager for ComfyUI XDev Nodes
# Simple but effective git workflow automation

param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("status", "commit", "sync", "help")]
    [string]$Action,
    
    [Parameter(Position = 1)]
    [string]$Message = ""
)

# Color functions
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "⚠️ $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ️ $msg" -ForegroundColor Cyan }

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Error "Not a git repository"
    exit 1
}

switch ($Action) {
    "status" {
        Write-Info "Git Status for XDev Nodes"
        Write-Host ""
        
        # Current branch
        $branch = git rev-parse --abbrev-ref HEAD 2>$null
        Write-Info "Current branch: $branch"
        
        # Check for changes
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
        
        # Recent commits
        Write-Host ""
        Write-Info "Recent commits:"
        git log --oneline -5 2>$null | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    }
    
    "commit" {
        if (-not $Message) {
            Write-Error "Commit message required. Use: git-manager.ps1 commit 'Your message'"
            exit 1
        }
        
        Write-Info "Creating intelligent commit for XDev Nodes..."
        
        # Stage all changes
        git add . 2>$null
        
        # Enhanced commit message
        $enhancedMessage = "XDev v0.6.0-advanced: $Message`n`n- Enhanced ComfyUI node toolkit with advanced AI capabilities`n- 67+ professional nodes including neural analysis, multimodal AI`n- Advanced performance monitoring and validation frameworks`n- Educational toolkit demonstrating ComfyUI best practices"
        
        # Create commit
        git commit -m $enhancedMessage 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Commit created successfully"
        } else {
            Write-Error "Commit failed"
        }
    }
    
    "sync" {
        Write-Info "Syncing with remote repository..."
        
        # Pull first
        Write-Host "Pulling latest changes..."
        git pull 2>$null
        
        # Push changes
        Write-Host "Pushing local changes..."
        git push 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Sync completed successfully"
        } else {
            Write-Warning "Sync completed with warnings"
        }
    }
    
    "help" {
        Write-Host ""
        Write-Info "Git Manager for ComfyUI XDev Nodes"
        Write-Host ""
        Write-Host "Available commands:"
        Write-Host "  status  - Show repository status and recent commits"
        Write-Host "  commit  - Create intelligent commit with message"
        Write-Host "  sync    - Pull and push changes"
        Write-Host "  help    - Show this help message"
        Write-Host ""
        Write-Host "Examples:"
        Write-Host "  .\git-manager.ps1 status"
        Write-Host "  .\git-manager.ps1 commit 'Added advanced AI nodes'"
        Write-Host "  .\git-manager.ps1 sync"
    }
}