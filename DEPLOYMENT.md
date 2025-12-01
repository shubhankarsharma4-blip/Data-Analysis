# GitHub Deployment Guide

## Pre-Deployment Checklist

### Code Quality
- [ ] Run tests locally: `pytest tests/`
- [ ] Check formatting: `black --check src/`
- [ ] Check imports: `isort --check-only src/`
- [ ] Lint code: `flake8 src/`
- [ ] Type hints: `mypy src/`

### Documentation
- [ ] Update README.md with any new features
- [ ] Update ARCHITECTURE.md if architecture changed
- [ ] Check all code comments are clear
- [ ] Verify docstrings are complete

### Testing
- [ ] Test on Windows: `python run_all.py`
- [ ] Test on macOS/Linux: `python run_all.py`
- [ ] Test dashboard: `streamlit run app.py`
- [ ] Verify exit codes: `$? -eq 0`

### Version Management
- [ ] Update version in `setup.py` and `pyproject.toml`
- [ ] Update CHANGELOG.md with release notes
- [ ] Tag release: `git tag v1.0.0`

---

## Step-by-Step Deployment to GitHub

### 1. Initialize Git Repository (First Time Only)

```bash
cd c:\Python\ecommerce_etl_project
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 2. Add All Files to Git

```bash
git add .
```

### 3. Create Initial Commit

```bash
git commit -m "feat: Initial release of E-commerce ETL pipeline v1.0.0"
```

### 4. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ecommerce-etl-project`
3. Description: `Production-grade ETL pipeline for e-commerce data`
4. Choose: Public (for open source) or Private (for internal use)
5. Click "Create repository"

### 5. Add Remote and Push

```bash
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-etl-project.git
git branch -M main
git push -u origin main
```

### 6. Create Development Branch

```bash
git checkout -b develop
git push -u origin develop
```

### 7. Set Up Branch Protection (Optional - GitHub UI)

1. Go to repository Settings → Branches
2. Click "Add rule" under "Branch protection rules"
3. Apply to: `main`
4. Require:
   - Pull request reviews before merging
   - Dismissal of stale PR reviews
   - Status checks to pass (CI/CD)
   - Branches to be up to date before merging

---

## Continuous Integration Setup

### GitHub Actions Workflows (Auto-Runs on Push)

The project includes 2 pre-configured workflows:

#### `.github/workflows/etl-tests.yml`
Runs on every push/PR:
- Tests pipeline on Windows, macOS, Linux
- Tests Python 3.9, 3.10, 3.11, 3.12, 3.13
- Runs linting (black, flake8, isort, mypy)
- Runs security scans (bandit, safety)

#### `.github/workflows/code-quality.yml`
Runs on every push/PR:
- Code coverage analysis
- Uploads to Codecov
- Documentation checks

### Enable Actions

1. Go to GitHub repository
2. Click "Actions" tab
3. Click "I understand my workflows, go ahead and enable them"

---

## Release Process

### Creating a Release

```bash
# 1. Update version numbers
# Edit: setup.py, pyproject.toml
VERSION="1.1.0"

# 2. Update changelog
# Add release notes to CHANGELOG.md

# 3. Commit version bump
git commit -am "chore: Bump version to $VERSION"

# 4. Create annotated tag
git tag -a v$VERSION -m "Release v$VERSION"

# 5. Push changes and tags
git push origin main
git push origin --tags

# 6. GitHub automatically creates release from tag
# View at: https://github.com/YOUR_USERNAME/ecommerce-etl-project/releases
```

### Creating GitHub Release (UI Method)

1. Go to repository → Releases
2. Click "Create a new release"
3. Tag version: `v1.1.0`
4. Release title: `v1.1.0 - Add incremental load support`
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

---

## Repository Structure for GitHub

```
ecommerce-etl-project/
├── .github/
│   └── workflows/
│       ├── etl-tests.yml       # Auto-run tests
│       └── code-quality.yml    # Code quality checks
├── .gitignore                  # Ignore .venv, logs, .db files
├── src/
│   ├── __init__.py            # Make src a package
│   ├── extract.py
│   ├── transform_staging.py
│   ├── transform_warehouse.py
│   ├── load.py
│   ├── validation.py
│   ├── pipeline.py
│   ├── logger_config.py
│   ├── incremental.py
│   └── config.py
├── tests/                      # Unit tests (add later)
│   ├── __init__.py
│   ├── test_extract.py
│   └── test_pipeline.py
├── docs/                       # Additional documentation
│   └── DEPLOYMENT.md
├── Data/
│   ├── Raw/
│   └── Processed/
├── logs/
│   └── .gitkeep               # Keep empty directory in git
├── README.md                  # Professional readme
├── ARCHITECTURE.md            # Technical architecture
├── CONTRIBUTING.md            # How to contribute
├── CODE_OF_CONDUCT.md         # Community standards
├── LICENSE                    # MIT license
├── setup.py                   # Package installation
├── pyproject.toml             # Package configuration
├── requirements.txt           # Dependencies
├── requirements-lock.txt      # Pinned versions
├── run_all.py                 # Main script
├── app.py                     # Streamlit app
└── CHANGELOG.md               # Version history
```

---

## Badges for README

Add these to your README.md for professional appearance:

```markdown
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://github.com/YOUR_USERNAME/ecommerce-etl-project/workflows/ETL%20Pipeline%20Tests/badge.svg)](https://github.com/YOUR_USERNAME/ecommerce-etl-project/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/ecommerce-etl-project/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/ecommerce-etl-project)
```

---

## Advanced GitHub Features

### Issues Template (`.github/ISSUE_TEMPLATE/bug_report.md`)

```markdown
---
name: Bug report
about: Create a report to help us improve
---

## Describe the bug
A clear and concise description of what the bug is.

## Steps to reproduce
1. Run `python run_all.py`
2. See error...

## Expected behavior
What should happen?

## Actual behavior
What actually happens?

## Environment
- OS: Windows 10
- Python: 3.13
- Branch: main

## Logs
Attach relevant log file from `logs/`
```

### Pull Request Template (`.github/PULL_REQUEST_TEMPLATE.md`)

```markdown
## Description
Brief description of changes

## Related Issues
Closes #123

## Changes Made
- [ ] Feature addition
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Code coverage maintained

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes
```

---

## Deployment to Production

### Option 1: Windows Task Scheduler

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "C:\Python\Python313\python.exe" `
  -Argument "C:\path\to\run_all.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 02:00
Register-ScheduledTask -TaskName "ETL-Pipeline" -Action $action `
  -Trigger $trigger -Principal (New-ScheduledTaskPrincipal -UserID "NT AUTHORITY\SYSTEM")
```

### Option 2: Docker Container

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["python", "run_all.py"]
```

```bash
docker build -t ecommerce-etl:latest .
docker push YOUR_REGISTRY/ecommerce-etl:latest
```

### Option 3: AWS Lambda

```python
import os
import sys
sys.path.insert(0, '/var/task')

from src.pipeline import run_pipeline
from src.config import Config

def lambda_handler(event, context):
    """ETL triggered by CloudWatch Events"""
    exit_code = run_pipeline(Config())
    return {
        "statusCode": 200 if exit_code == 0 else 500,
        "body": f"ETL completed with code {exit_code}"
    }
```

---

## Monitoring & Alerts

### GitHub Actions Notifications

Enable in repository Settings → Notifications:
- [ ] On completed workflow runs
- [ ] On workflow run failure

### Email Alerts on Failure

```powershell
# After scheduled task runs
if ($LASTEXITCODE -ne 0) {
    # Send email alert
    Send-MailMessage -To "ops@example.com" `
      -From "etl@example.com" `
      -Subject "ETL Pipeline Failed" `
      -Body (Get-Content logs/etl_latest.log) `
      -SmtpServer "smtp.gmail.com"
}
```

---

## Troubleshooting GitHub Deployment

### Tests Failing on GitHub Actions

1. Check "Actions" tab for detailed logs
2. Run same test locally: `python run_all.py`
3. Common issues:
   - Missing dependencies in `requirements.txt`
   - Path issues (use `Path` not hardcoded paths)
   - OS-specific issues (test on multiple OS)

### Large Files in Git

If you accidentally committed large files:

```bash
# Remove from git history
git rm --cached Data/ecommerce.db
echo "ecommerce.db" >> .gitignore
git commit -am "Remove large database file"

# For truly removing from history (destructive):
git filter-branch --tree-filter 'rm -f Data/ecommerce.db' HEAD
```

---

## Summary

✅ **Your ETL pipeline is now GitHub-ready with:**
- Professional README and documentation
- License (MIT)
- Contribution guidelines
- Code of Conduct
- Automated testing (GitHub Actions)
- Code quality checks
- Security scanning
- Branch protection
- Release management
- Multiple deployment options

**Next steps:**
1. Create GitHub account if not already done
2. Follow "Step-by-Step Deployment" above
3. Watch GitHub Actions run automatically
4. Invite collaborators from Settings → Collaborators

**For support:** Open an issue on GitHub or check CONTRIBUTING.md
