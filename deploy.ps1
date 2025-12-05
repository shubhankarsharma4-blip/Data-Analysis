# PowerShell script to help deploy to Streamlit Cloud
# This script helps you push your code to GitHub

Write-Host "🚀 Streamlit Cloud Deployment Helper" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "⚠️  Git not initialized. Initializing now..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git initialized" -ForegroundColor Green
}

# Check if remote exists
$remoteExists = git remote | Select-String -Pattern "origin"
if (-not $remoteExists) {
    Write-Host ""
    Write-Host "📝 GitHub Repository Setup Required" -ForegroundColor Yellow
    Write-Host "-----------------------------------" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Before running this script, you need to:" -ForegroundColor White
    Write-Host "1. Create a GitHub repository at: https://github.com/new" -ForegroundColor White
    Write-Host "2. Copy the repository URL (e.g., https://github.com/YOUR_USERNAME/repo-name.git)" -ForegroundColor White
    Write-Host ""
    $repoUrl = Read-Host "Enter your GitHub repository URL (or press Enter to skip)"
    
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "✅ Remote added: $repoUrl" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Skipping remote setup. You can add it later with:" -ForegroundColor Yellow
        Write-Host "   git remote add origin YOUR_REPO_URL" -ForegroundColor White
    }
}

# Check for uncommitted changes
Write-Host ""
Write-Host "📋 Checking for changes..." -ForegroundColor Cyan
$status = git status --porcelain

if ($status) {
    Write-Host "✅ Found changes to commit" -ForegroundColor Green
    Write-Host ""
    
    # Add all files
    Write-Host "📦 Adding files to git..." -ForegroundColor Cyan
    git add .
    Write-Host "✅ Files added" -ForegroundColor Green
    
    # Commit
    Write-Host ""
    $commitMessage = Read-Host "Enter commit message (or press Enter for default)"
    if (-not $commitMessage) {
        $commitMessage = "Deploy to Streamlit Cloud"
    }
    
    git commit -m $commitMessage
    Write-Host "✅ Changes committed" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No changes to commit" -ForegroundColor Blue
}

# Push to GitHub
Write-Host ""
$push = Read-Host "Push to GitHub? (Y/N)"
if ($push -eq "Y" -or $push -eq "y") {
    Write-Host ""
    Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Cyan
    
    # Check if main branch exists
    $branch = git branch --show-current
    if (-not $branch) {
        git branch -M main
        $branch = "main"
    }
    
    git push -u origin $branch
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 Next Steps:" -ForegroundColor Cyan
        Write-Host "1. Go to: https://share.streamlit.io" -ForegroundColor White
        Write-Host "2. Sign in with GitHub" -ForegroundColor White
        Write-Host "3. Click 'New app'" -ForegroundColor White
        Write-Host "4. Select your repository and 'streamlit_app.py'" -ForegroundColor White
        Write-Host "5. Click 'Deploy'" -ForegroundColor White
        Write-Host ""
        Write-Host "📖 See DEPLOY_TO_STREAMLIT_CLOUD.md for detailed instructions" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "❌ Error pushing to GitHub" -ForegroundColor Red
        Write-Host "Check your GitHub credentials and repository URL" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "ℹ️  Skipping push. You can push manually with:" -ForegroundColor Blue
    Write-Host "   git push -u origin main" -ForegroundColor White
}

Write-Host ""
Write-Host "✨ Done!" -ForegroundColor Green

