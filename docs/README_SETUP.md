# Fruit Quality Scanner - Setup Guide

## Quick Start

### Option 1: Automated Setup (Recommended)

**For PowerShell:**
```powershell
.\setup_venv.ps1
```

**For Command Prompt:**
```cmd
setup_venv.bat
```

The script will:
1. Check for Python 3.11 or 3.12
2. Create a virtual environment (`.venv`)
3. Install all dependencies
4. Provide instructions to run the application

### Option 2: Manual Setup

#### Step 1: Install Python 3.11 or 3.12

Download and install Python 3.11 or 3.12 from:
- https://www.python.org/downloads/

**Important:** Python 3.13 is not yet supported by PyTorch. Use Python 3.11 or 3.12.

#### Step 2: Create Virtual Environment

**PowerShell:**
```powershell
# Using Python 3.11
python3.11 -m venv .venv
# OR using Python Launcher
py -3.11 -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
# Using Python 3.11
python3.11 -m venv .venv
# OR using Python Launcher
py -3.11 -m venv .venv

# Activate
.venv\Scripts\activate.bat
```

#### Step 3: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Run the Application

```powershell
python app.py
```

The application will be available at: **http://localhost:5000**

## Troubleshooting

### Python Version Issues

If you get errors about PyTorch not being available:
- **Problem:** Python 3.13 is too new
- **Solution:** Use Python 3.11 or 3.12

### Virtual Environment Issues

If activation fails:
- **PowerShell:** You may need to set execution policy:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Missing Dependencies

If some packages fail to install:
1. Make sure you're using Python 3.11 or 3.12
2. Try upgrading pip: `pip install --upgrade pip`
3. Install packages individually to identify problematic ones

### Database Connection

The application uses SQLite by default (no setup required). For PostgreSQL or MySQL:
1. Create a `.env` file in the project root
2. Set `DATABASE_TYPE=postgresql` or `DATABASE_TYPE=mysql`
3. Configure connection settings in `.env`

## System Requirements

- **Python:** 3.11 or 3.12 (3.13 not supported yet)
- **Operating System:** Windows 10/11
- **RAM:** 4GB minimum (8GB recommended for YOLO)
- **Storage:** 2GB free space for dependencies

## Next Steps

After setup:
1. Open http://localhost:5000 in your browser
2. Upload a fruit image to test detection
3. View results with bounding boxes and quality analysis

For more information, see the main README.md file.

