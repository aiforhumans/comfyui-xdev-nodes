#!/usr/bin/env powershell
<#
.SYNOPSIS
    Advanced Git Repository Management for ComfyUI XDev Nodes
    
.DESCRIPTION
    Comprehensive git operations including:
    - Repository status analysis
    - Intelligent staging and commits
    - Branch management
    - Remote synchronization
    - Version tagging
    - Advanced conflict resolution
    
.PARAMETER Operation
    Git operation to perform
    
.PARAMETER Message
    Commit message for staging operations
    
.PARAMETER Force
    Force operation (use with caution)
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("status", "stage_all", "commit", "push", "pull", "sync", "tag_version", "cleanup", "advanced_commit", "create_branch", "merge_branch")]
    [string]$Operation,
    
    [Parameter(Mandatory=$false)]
    [string]$Message = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# Color output functions
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "⚠️ $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ️ $msg" -ForegroundColor Cyan }
function Write-Header { param($msg) Write-Host "`n🚀 $msg" -ForegroundColor Magenta -BackgroundColor Black }

# Main script
try {
    Write-Header "XDev Nodes - Advanced Git Manager v2.0"
    
    # Verify we're in a git repository
    if (-not (Test-Path ".git")) {
        Write-Error "Not in a git repository. Initializing..."
        git init
        Write-Success "Git repository initialized"
    }
    
    # Get current repository status
    $gitStatus = git status --porcelain 2>$null
    $gitBranch = git branch --show-current 2>$null
    $gitRemote = git remote -v 2>$null
    
    Write-Info "Current branch: $gitBranch"
    if ($gitRemote) {
        Write-Info "Remote configured: $(($gitRemote -split "`n")[0])"
    } else {
        Write-Warning "No remote repository configured"
    }
    
    switch ($Operation) {
        "status" {
            Write-Header "Repository Status Analysis"
            
            if ($gitStatus) {
                Write-Info "Changes detected:"
                foreach ($line in $gitStatus) {
                    $status = $line.Substring(0, 2)
                    $file = $line.Substring(3)
                    
                    switch ($status.Trim()) {
                        "M" { Write-Host "  📝 Modified: $file" -ForegroundColor Yellow }
                        "A" { Write-Host "  ➕ Added: $file" -ForegroundColor Green }
                        "D" { Write-Host "  ➖ Deleted: $file" -ForegroundColor Red }
                        "??" { Write-Host "  ❓ Untracked: $file" -ForegroundColor Gray }
                        "MM" { Write-Host "  🔄 Modified (staged+unstaged): $file" -ForegroundColor Magenta }
                        default { Write-Host "  📄 $status`: $file" -ForegroundColor White }
                    }
                }
                
                # File statistics
                $modifiedCount = ($gitStatus | Where-Object { $_ -match "^.M" }).Count
                $addedCount = ($gitStatus | Where-Object { $_ -match "^A" }).Count
                $deletedCount = ($gitStatus | Where-Object { $_ -match "^.D" }).Count
                $untrackedCount = ($gitStatus | Where-Object { $_ -match "^\?\?" }).Count
                
                Write-Info "Summary: $modifiedCount modified, $addedCount added, $deletedCount deleted, $untrackedCount untracked"
                
                # Check for large files
                $largeFiles = Get-ChildItem -Recurse -File | Where-Object { $_.Length -gt 10MB -and $_.Name -notmatch "\.(git|zip|tar|gz)$" }
                if ($largeFiles) {
                    Write-Warning "Large files detected (>10MB):"
                    foreach ($file in $largeFiles) {
                        $sizeMB = [math]::Round($file.Length / 1MB, 2)
                        Write-Host "    📦 $($file.FullName) ($sizeMB MB)" -ForegroundColor Yellow
                    }
                }
            } else {
                Write-Success "Working directory clean - no changes detected"
            }
            
            # Show recent commits
            Write-Info "`nRecent commits:"
            git log --oneline -5 2>$null | ForEach-Object {
                Write-Host "  🔸 $_" -ForegroundColor Gray
            }
        }
        
        "stage_all" {
            Write-Header "Staging All Changes"
            
            if ($gitStatus) {
                # Add all files
                git add -A
                Write-Success "All changes staged"
                
                # Show what was staged
                $stagedFiles = git diff --cached --name-only
                Write-Info "Staged files:"
                foreach ($file in $stagedFiles) {
                    Write-Host "  ✅ $file" -ForegroundColor Green
                }
            } else {
                Write-Warning "No changes to stage"
            }
        }
        
        "commit" {
            Write-Header "Creating Commit"
            
            if (-not $Message) {
                Write-Error "Commit message required. Use -Message parameter"
                exit 1
            }
            
            # Check if there are staged changes
            $stagedChanges = git diff --cached --name-only
            if (-not $stagedChanges) {
                Write-Warning "No staged changes. Staging all changes first..."
                git add -A
                $stagedChanges = git diff --cached --name-only
            }
            
            if ($stagedChanges) {
                # Create enhanced commit message
                $enhancedMessage = @"
$Message

Changes in this commit:
$(foreach ($file in $stagedChanges) { "- $file" }) -join "`n")

Timestamp: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
XDev Nodes Version: v0.6.0-advanced
"@
                
                git commit -m $enhancedMessage
                Write-Success "Commit created successfully"
                
                # Show commit hash
                $commitHash = git rev-parse HEAD
                Write-Info "Commit hash: $($commitHash.Substring(0, 8))"
            } else {
                Write-Warning "No changes to commit"
            }
        }
        
        "advanced_commit" {
            Write-Header "Advanced Commit with Auto-categorization"
            
            if (-not $gitStatus) {
                Write-Warning "No changes to commit"
                return
            }
            
            # Auto-categorize changes
            $categories = @{
                "feat" = @()
                "fix" = @()
                "docs" = @()
                "style" = @()
                "refactor" = @()
                "test" = @()
                "chore" = @()
            }
            
            foreach ($line in $gitStatus) {
                $file = $line.Substring(3)
                
                if ($file -match "\.(md|txt|rst)$") {
                    $categories["docs"] += $file
                } elseif ($file -match "test|spec") {
                    $categories["test"] += $file
                } elseif ($file -match "\.(py|js|ts|css|scss)$") {
                    if ($file -match "node") {
                        $categories["feat"] += $file
                    } else {
                        $categories["refactor"] += $file
                    }
                } elseif ($file -match "\.(json|yaml|yml|toml)$") {
                    $categories["chore"] += $file
                } else {
                    $categories["chore"] += $file
                }
            }
            
            # Generate commit message
            $commitParts = @()
            foreach ($category in $categories.Keys) {
                if ($categories[$category].Count -gt 0) {
                    $commitParts += "$category($($categories[$category].Count))"
                }
            }
            
            $autoMessage = if ($Message) { $Message } else { "Advanced updates: $($commitParts -join ', ')" }
            
            git add -A
            git commit -m $autoMessage
            Write-Success "Advanced commit created: $autoMessage"
        }
        
        "push" {
            Write-Header "Pushing to Remote Repository"
            
            if (-not $gitRemote) {
                Write-Error "No remote repository configured. Set up remote first:"
                Write-Info "git remote add origin <repository-url>"
                exit 1
            }
            
            # Check for uncommitted changes
            if ($gitStatus) {
                Write-Warning "Uncommitted changes detected. Commit first or use -Force"
                if (-not $Force) {
                    exit 1
                }
            }
            
            # Push with detailed output
            Write-Info "Pushing to remote repository..."
            git push origin $gitBranch --progress
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Push completed successfully"
            } else {
                Write-Error "Push failed. Check network connection and credentials"
            }
        }
        
        "pull" {
            Write-Header "Pulling from Remote Repository"
            
            if (-not $gitRemote) {
                Write-Error "No remote repository configured"
                exit 1
            }
            
            # Check for local changes
            if ($gitStatus -and -not $Force) {
                Write-Warning "Local changes detected. Stash or commit first, or use -Force"
                exit 1
            }
            
            Write-Info "Pulling from remote repository..."
            git pull origin $gitBranch --progress
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Pull completed successfully"
            } else {
                Write-Error "Pull failed. Check for conflicts"
            }
        }
        
        "sync" {
            Write-Header "Full Repository Synchronization"
            
            # Stage all changes
            if ($gitStatus) {
                Write-Info "Staging all changes..."
                git add -A
            }
            
            # Commit if there are staged changes
            $stagedChanges = git diff --cached --name-only
            if ($stagedChanges) {
                $syncMessage = if ($Message) { $Message } else { "Auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }
                git commit -m $syncMessage
                Write-Success "Changes committed: $syncMessage"
            }
            
            # Pull from remote
            if ($gitRemote) {
                Write-Info "Pulling from remote..."
                git pull origin $gitBranch --rebase
            }
            
            # Push to remote
            if ($gitRemote) {
                Write-Info "Pushing to remote..."
                git push origin $gitBranch
                Write-Success "Repository synchronized"
            }
        }
        
        "tag_version" {
            Write-Header "Version Tagging"
            
            $version = if ($Message) { $Message } else { "v0.6.0-advanced" }
            
            # Create annotated tag
            $tagMessage = @"
XDev Nodes $version

Features:
- 42+ professional ComfyUI nodes
- Advanced AI analysis and orchestration
- Multimodal AI integration
- Performance optimization framework
- Professional face swapping
- Advanced data analytics

Release Date: $(Get-Date -Format "yyyy-MM-dd")
"@
            
            git tag -a $version -m $tagMessage
            Write-Success "Version tag created: $version"
            
            # Push tag to remote
            if ($gitRemote) {
                git push origin $version
                Write-Success "Tag pushed to remote"
            }
        }
        
        "cleanup" {
            Write-Header "Repository Cleanup"
            
            # Clean untracked files
            Write-Info "Cleaning untracked files..."
            git clean -fd
            
            # Prune remote branches
            if ($gitRemote) {
                Write-Info "Pruning remote branches..."
                git remote prune origin
            }
            
            # Garbage collection
            Write-Info "Running garbage collection..."
            git gc --prune=now
            
            # Show repository size
            $gitSize = (Get-ChildItem .git -Recurse | Measure-Object -Property Length -Sum).Sum
            $gitSizeMB = [math]::Round($gitSize / 1MB, 2)
            Write-Info "Repository size: $gitSizeMB MB"
            
            Write-Success "Repository cleanup completed"
        }
        
        "create_branch" {
            Write-Header "Creating New Branch"
            
            if (-not $Message) {
                Write-Error "Branch name required. Use -Message parameter"
                exit 1
            }
            
            $branchName = $Message
            
            # Check if branch already exists
            $existingBranch = git branch --list $branchName
            if ($existingBranch) {
                Write-Warning "Branch '$branchName' already exists"
                if (-not $Force) {
                    exit 1
                }
            }
            
            # Create and switch to new branch
            git checkout -b $branchName
            Write-Success "Created and switched to branch: $branchName"
            
            # Push to remote if configured
            if ($gitRemote) {
                git push -u origin $branchName
                Write-Success "Branch pushed to remote with upstream tracking"
            }
        }
        
        "merge_branch" {
            Write-Header "Merging Branch"
            
            if (-not $Message) {
                Write-Error "Source branch name required. Use -Message parameter"
                exit 1
            }
            
            $sourceBranch = $Message
            
            # Verify source branch exists
            $branchExists = git branch --list $sourceBranch
            if (-not $branchExists) {
                Write-Error "Source branch '$sourceBranch' does not exist"
                exit 1
            }
            
            # Check for uncommitted changes
            if ($gitStatus -and -not $Force) {
                Write-Warning "Uncommitted changes detected. Commit first or use -Force"
                exit 1
            }
            
            # Perform merge
            Write-Info "Merging $sourceBranch into $gitBranch..."
            git merge $sourceBranch --no-ff
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Branch merged successfully"
                
                # Ask if user wants to delete source branch
                $deleteChoice = Read-Host "Delete source branch '$sourceBranch'? (y/N)"
                if ($deleteChoice -eq 'y' -or $deleteChoice -eq 'Y') {
                    git branch -d $sourceBranch
                    Write-Success "Source branch deleted"
                }
            } else {
                Write-Error "Merge failed. Resolve conflicts manually"
            }
        }
        
        default {
            Write-Error "Unknown operation: $Operation"
            exit 1
        }
    }
    
    Write-Success "Git operation completed successfully!"
    
} catch {
    Write-Error "Script execution failed: $($_.Exception.Message)"
    Write-Info "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

# Final status summary
Write-Header "Final Repository Status"
$finalStatus = git status --porcelain 2>$null
if ($finalStatus) {
    Write-Info "$(($finalStatus | Measure-Object).Count) files with changes"
} else {
    Write-Success "Working directory clean"
}

$lastCommit = git log --oneline -1 2>$null
if ($lastCommit) {
    Write-Info "Latest commit: $lastCommit"
}

Write-Info "Current branch: $(git branch --show-current 2>$null)"
Write-Success "XDev Nodes Git Manager completed! 🎉"