# Repository Structure Guide

This document describes the organization and purpose of each directory and file in the FscanV2 repository.

## 📂 Directory Structure

### Root Level Files

- **`app.py`** - Main Flask application entry point
- **`config.py`** - Centralized configuration management
- **`requirements.txt`** - Python package dependencies
- **`README.md`** - Main project documentation

### `/docs` - Documentation

All project documentation files:
- `API_DOCUMENTATION.md` - API endpoint documentation
- `PHASE2_BACKEND.md` - Backend architecture details
- `PHASE2_SUMMARY.md` - Project phase summary
- `README_SETUP.md` - Detailed setup instructions
- `STRUCTURE.md` - This file

### `/scripts` - Utility Scripts

Scripts for dataset management, training, and application execution:
- `auto_label_dataset.py` - Auto-label images and organize into YOLO format
- `train_yolov5.py` - YOLOv5n model training script with pause/resume
- `run_app.bat` - Windows batch script to run the application
- `run_app.ps1` - PowerShell script to run the application
- `optimize_gpu_performance.bat` - GPU optimization script

### `/data` - Data and Models (Git-ignored)

Contains datasets and trained models (not version controlled):

#### `/data/datasets`
- `Fruit_dataset/` - YOLO-formatted dataset
  - `data.yaml` - Dataset configuration
  - `classes.txt` - Class names list
  - `train/`, `val/`, `test/` - Split datasets with images and labels

#### `/data/models`
- `yolov5n/` - YOLOv5n trained models
  - `Datasets YOLOv5n/` - Training outputs and weights
    - `runs/train/yolov5n_fruit_ripeness/` - Training results
    - `weights/best.pt` - Best model weights
    - `yolov5nu.pt` - Pretrained base model

### `/models` - Application Models (Source Code)

Python modules for detection and fusion:
- `yolo_detector.py` - YOLO detection wrapper
- `fusion_engine.py` - YOLO + NIR fusion logic
- `__init__.py` - Package initialization

### `/database` - Database Layer

Database handling and persistence:
- `db_handler.py` - Database operations (SQLite/PostgreSQL/MySQL)
- `fruit_scanner.db` - SQLite database file (created at runtime)
- `__init__.py` - Package initialization

### `/nir` - NIR Scanner Integration

Near-infrared scanner integration:
- `nir_scanner.py` - NIR scanner interface
- `__init__.py` - Package initialization

### `/static` - Static Web Assets

Frontend assets served by Flask:
- `/css` - Stylesheets
- `/js` - JavaScript files
- `/images` - Image uploads and processed images

### `/templates` - HTML Templates

Flask Jinja2 templates:
- `index.html` - Main application page
- `results.html` - Results display page

### `/tests` - Unit Tests

Test files (to be implemented):
- Placeholder for future test suite

## 🔄 File Path References

### Configuration Paths (config.py)

- **Model Path**: `data/models/yolov5n/Datasets YOLOv5n/runs/train/yolov5n_fruit_ripeness/weights/best.pt`
- **Dataset Config**: `data/datasets/Fruit_dataset/data.yaml`
- **Upload Folder**: `static/images/uploads/`
- **Processed Folder**: `static/images/processed/`
- **Database**: `database/fruit_scanner.db`

### Script Defaults

- **auto_label_dataset.py**: Default dataset path is `data/datasets/Fruit_dataset`
- **train_yolov5.py**: Default data path is `../data/datasets/Fruit_dataset/data.yaml`

## 📝 Best Practices

1. **Data Organization**: All datasets and models go in `/data` (git-ignored)
2. **Documentation**: All docs go in `/docs`
3. **Scripts**: All utility scripts go in `/scripts`
4. **Source Code**: Application modules stay in root-level packages (`/models`, `/database`, `/nir`)
5. **Static Files**: Web assets in `/static`, templates in `/templates`

## 🔧 Maintenance

When adding new features:
- Add documentation to `/docs`
- Add utility scripts to `/scripts`
- Keep source code modules organized in their respective packages
- Update this document if structure changes significantly

