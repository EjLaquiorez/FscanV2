# GitHub Setup Instructions

## Repository Status

✅ Git repository initialized  
✅ Essential files committed  
✅ Non-essential files excluded via .gitignore  

## What's Included

This repository contains all essential files needed to run the web-based fruit scanner on another computer:

- **Core Application**: `app.py`, `config.py`
- **Source Code**: `models/`, `database/`, `nir/`
- **Web Interface**: `templates/`, `static/css/`, `static/js/`
- **Scripts**: Training, auto-labeling, and run scripts
- **Configuration**: `requirements.txt`, `README.md`, `.gitignore`
- **Documentation**: API docs, setup guides, architecture docs

## What's Excluded

The following are **NOT** included (as they should be):

- ❌ Thesis documents (`docs/docs/*.docx`, thesis markdown files)
- ❌ Processed/uploaded images (user-generated content)
- ❌ Database files (created automatically on first run)
- ❌ Model weights (`.pt` files - users must train or download separately)
- ❌ Dataset files (large, users provide their own)
- ❌ Expense files (`THESIS_PROJECT_EXPENSES.txt`)
- ❌ Python cache files (`__pycache__/`)

## Next Steps: Push to GitHub

### 1. Create a New Repository on GitHub

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Name it (e.g., `FscanV2` or `fruit-quality-scanner`)
4. **Do NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

### 2. Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```powershell
# Add the remote repository (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename branch to 'main' (if GitHub uses 'main' instead of 'master')
git branch -M main

# Push your code
git push -u origin main
```

Or if your repository uses `master`:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin master
```

### 3. Verify Upload

1. Refresh your GitHub repository page
2. You should see all your files listed
3. Verify that excluded files (thesis docs, database, etc.) are NOT visible

## Deployment on Another Computer

### Quick Setup

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Important Notes for Deployment

1. **Model Weights**: You'll need to either:
   - Train your own model using `scripts/train_yolov5.py`
   - Download pre-trained weights and place them in the appropriate location
   - Update `config.py` to point to your model file

2. **Database**: The SQLite database (`database/fruit_scanner.db`) will be created automatically on first run

3. **Directories**: The `static/images/processed/` and `static/images/uploads/` directories will be created automatically (they're tracked via `.gitkeep` files)

4. **Configuration**: Review `config.py` and adjust settings as needed for your environment

## Repository Statistics

- **Total files tracked**: 35 files
- **Initial commit**: `d23d9ad` - Essential files for web-based fruit scanner deployment
- **Directory structure commit**: `69c8c0e` - Added .gitkeep files

## Troubleshooting

### If you see excluded files in GitHub

Check your `.gitignore` file and ensure patterns are correct. Files already tracked before adding to `.gitignore` need to be removed:

```powershell
git rm --cached filename
git commit -m "Remove excluded file"
```

### If directories are missing after clone

The `.gitkeep` files ensure empty directories are preserved. If directories are missing, they'll be created when the application runs for the first time.

### If model files are needed

Model weights (`.pt` files) are intentionally excluded due to size. Users should:
1. Train their own model using provided scripts
2. Or download pre-trained weights separately
3. Place them in the location specified in `config.py`

