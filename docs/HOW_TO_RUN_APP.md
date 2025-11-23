# How to Start the Flask Application

This guide shows you different ways to start the Fruit Quality Scanner Flask application.

## ⚠️ IMPORTANT: Always Activate Virtual Environment First!

**Common Error:** If you run `python app.py` directly without activating the virtual environment, you'll get errors like:
```
ModuleNotFoundError: No module named 'click.core'
```

**Why?** You're using system Python instead of the virtual environment Python with all the installed packages.

**Solution:** Always activate the virtual environment first (see Method 3 below) or use the provided scripts.

## Prerequisites

1. **Virtual Environment**: Make sure you have the `.venv_yolo` virtual environment set up
2. **Dependencies**: Install all required packages with `pip install -r requirements.txt`

## Method 1: Using Batch Script (Easiest - Windows)

### Option A: Double-click
Simply double-click the `run_app_simple.bat` file in Windows Explorer.

### Option B: Command Prompt
```cmd
run_app_simple.bat
```

**What it does:**
- Activates the virtual environment automatically
- Runs `python app.py`
- Keeps the window open after the app stops

---

## Method 2: Using PowerShell Script

### Option A: Right-click and "Run with PowerShell"
Right-click `run_app_simple.ps1` → "Run with PowerShell"

### Option B: PowerShell Command
```powershell
.\run_app_simple.ps1
```

**What it does:**
- Activates the virtual environment automatically
- Runs `python app.py`
- Shows colored output

---

## Method 3: Manual Activation (Recommended for Learning)

### Step-by-Step Process

#### In Command Prompt (CMD):
```cmd
REM 1. Navigate to project directory (if not already there)
cd "D:\THESIS PROJECT\FscanV2"

REM 2. Activate virtual environment
.venv_yolo\Scripts\activate.bat

REM 3. Run the app
python app.py
```

#### In PowerShell:
```powershell
# 1. Navigate to project directory (if not already there)
cd "D:\THESIS PROJECT\FscanV2"

# 2. Activate virtual environment
.\.venv_yolo\Scripts\Activate.ps1

# 3. Run the app
python app.py
```

**What you'll see:**
```
============================================================
Initializing Fruit Quality Scanner...
============================================================
YOLO detector initialized successfully
Database handler initialized successfully
============================================================

Starting Flask server on 0.0.0.0:5000
Debug mode: True
Access the application at: http://localhost:5000

 * Running on http://127.0.0.1:5000
```

---

## Method 4: Direct Python Command (If venv is in PATH)

```powershell
.\.venv_yolo\Scripts\python.exe app.py
```

This directly uses the Python interpreter from the virtual environment without activating it first.

---

## Method 5: Using Python Module (Alternative)

```powershell
.\.venv_yolo\Scripts\python.exe -m flask run
```

---

## Understanding the Process

### 1. **Virtual Environment Activation**
- **Why?** Isolates project dependencies from system Python
- **What it does:** Changes your Python interpreter to use packages from `.venv_yolo`
- **How to verify:** After activation, you'll see `(.venv_yolo)` in your prompt

### 2. **Running app.py**
- **What happens:**
  1. Flask app initializes
  2. YOLO detector loads the trained model
  3. Database connection is established
  4. Server starts on port 5000

### 3. **Accessing the App**
- Open your browser and go to: **http://localhost:5000**
- The app will be available until you stop it (Ctrl+C)

---

## Stopping the Application

### Method 1: Keyboard Shortcut
Press `Ctrl+C` in the terminal where the app is running

### Method 2: Close Terminal
Simply close the terminal window (not recommended - may leave processes running)

### Method 3: Task Manager (If stuck)
1. Open Task Manager (Ctrl+Shift+Esc)
2. Find `python.exe` processes
3. End the process

---

## Troubleshooting

### Problem: "python is not recognized" or "ModuleNotFoundError: No module named 'click.core'"
**Solution:** You're using system Python instead of virtual environment Python!

**Fix:**
1. **Activate the virtual environment first:**
   ```powershell
   .\.venv_yolo\Scripts\Activate.ps1
   ```
   You should see `(.venv_yolo)` in your prompt.

2. **Then run the app:**
   ```powershell
   python app.py
   ```

3. **Or use the full path directly:**
   ```powershell
   .\.venv_yolo\Scripts\python.exe app.py
   ```

**How to verify:** After activation, check which Python you're using:
```powershell
where.exe python
# Should show: D:\THESIS PROJECT\FscanV2\.venv_yolo\Scripts\python.exe
```

### Problem: "ModuleNotFoundError"
**Solution:** Install dependencies:
```powershell
.\.venv_yolo\Scripts\pip.exe install -r requirements.txt
```

### Problem: "Port 5000 already in use"
**Solution:** 
1. Stop the existing app (Ctrl+C)
2. Or change the port in `config.py`:
   ```python
   PORT = int(os.getenv('PORT', 5001))  # Change to 5001
   ```

### Problem: "Model file not found"
**Solution:** Check that the model path in `config.py` is correct:
```python
MODEL_PATH = BASE_DIR / 'data' / 'models' / 'yolov5n' / 'runs' / 'train' / 'yolov5n_fruit_ripeness' / 'weights' / 'best.pt'
```

---

## Quick Reference

| Method | Command | Best For |
|--------|---------|----------|
| Batch Script | `run_app_simple.bat` | Quick start, Windows users |
| PowerShell Script | `.\run_app_simple.ps1` | Quick start, PowerShell users |
| Manual CMD | `activate.bat` then `python app.py` | Learning, debugging |
| Manual PowerShell | `Activate.ps1` then `python app.py` | Learning, debugging |
| Direct Python | `.\venv_yolo\Scripts\python.exe app.py` | Scripts, automation |

---

## Tips

1. **Keep the terminal open** - The app runs in the foreground, so don't close the terminal
2. **Check the output** - Look for initialization messages to ensure everything loaded correctly
3. **Use Ctrl+C** - Always stop the app properly with Ctrl+C before closing
4. **Clear cache** - If you make code changes, restart the app or run `clear_cache.bat`

---

## Next Steps

After starting the app:
1. Open http://localhost:5000 in your browser
2. Upload a fruit image to test detection
3. View the results with proper fruit type and ripeness display

Happy coding! 🍎🍌🥭

