# FscanV2 — Fruit Quality Scanner

A professional fruit ripeness detection application using YOLOv5n deep learning model. This application can identify and classify fruit ripeness levels (fresh, ripe, unripe, overripe, rotten) for various fruits including bananas, mangoes, cashews, and cacao.

## 📁 Repository Structure

```
FscanV2/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
│
├── docs/                  # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── PHASE2_BACKEND.md
│   ├── PHASE2_SUMMARY.md
│   └── README_SETUP.md
│
├── scripts/               # Utility scripts
│   ├── auto_label_dataset.py    # Auto-label images for YOLO
│   ├── train_yolov5.py          # YOLOv5n training script
│   ├── run_app.bat              # Windows batch script to run app
│   ├── run_app.ps1              # PowerShell script to run app
│   └── optimize_gpu_performance.bat
│
├── data/                  # Data and models (git-ignored)
│   ├── datasets/
│   │   └── Fruit_dataset/        # YOLO dataset structure
│   │       ├── data.yaml
│   │       ├── classes.txt
│   │       ├── train/
│   │       ├── val/
│   │       └── test/
│   └── models/
│       └── yolov5n/              # Trained YOLOv5n models
│           └── Datasets YOLOv5n/
│               ├── runs/
│               └── yolov5nu.pt
│
├── models/                # Application models (source code)
│   ├── yolo_detector.py
│   └── fusion_engine.py
│
├── database/              # Database handlers
│   └── db_handler.py
│
├── nir/                   # NIR scanner integration
│   └── nir_scanner.py
│
├── static/                # Static web assets
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/             # HTML templates
│   ├── index.html
│   └── results.html
│
└── tests/                 # Unit tests (to be implemented)
```

## 🚀 Quick Start

### 1. Environment Setup

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Optional: Install CUDA PyTorch for GPU support
# pip install --index-url https://download.pytorch.org/whl/cu121 torch torchvision torchaudio
```

### 2. Run the Application

**Option A: Using provided scripts**
```powershell
# PowerShell
.\scripts\run_app.ps1

# Or Windows Batch
.\scripts\run_app.bat
```

**Option B: Direct Python**
```powershell
python app.py
```

The application will be available at `http://localhost:5000`

## 📊 Dataset Structure

The dataset is organized for Ultralytics YOLO format:

```
data/datasets/Fruit_dataset/
├── data.yaml              # Dataset configuration
├── classes.txt            # Class names
├── train/
│   ├── images/           # Training images
│   └── labels/           # YOLO format labels
├── val/
│   ├── images/           # Validation images
│   └── labels/           # YOLO format labels
└── test/
    ├── images/           # Test images
    └── labels/           # YOLO format labels
```

### Supported Classes (12 classes)

- Fresh Banana
- Rotten Banana
- Half-Ripe Mango
- OverRipe Mango
- Ripe Mango
- Unripe Mango
- Unripe Cashew
- Ripe Cashew
- OverRipe Cashew
- Cacao Overripe
- Cacao Ripe
- Cacao Underripe

## 🎯 Training YOLOv5n Model

### Using the Training Script

```powershell
# From repository root
cd scripts
python train_yolov5.py --epochs 60 --batch 16 --imgsz 640

# Resume from checkpoint
python train_yolov5.py --resume
```

### Using Ultralytics CLI

```powershell
yolo task=detect mode=train \
    data=data/datasets/Fruit_dataset/data.yaml \
    model=yolov5nu.pt \
    epochs=50 \
    imgsz=640 \
    batch=16
```

Training outputs are saved to `data/models/yolov5n/Datasets YOLOv5n/runs/train/`

## 🔧 Auto-Labeling Images

Add new images to the dataset with automatic placeholder labels:

```powershell
# Add a new class with 80/10/10 train/val/test split
python scripts/auto_label_dataset.py \
    --src FreshBanana \
    --class-name "Fresh Banana" \
    --dst data/datasets/Fruit_dataset \
    --split 0.8 0.1 0.1

# Flat mode (no split)
python scripts/auto_label_dataset.py \
    --src SomeFolder \
    --class-name "Some Class" \
    --dst data/datasets/Fruit_dataset \
    --mode flat
```

## 🧪 Validation and Testing

```powershell
# Validate on validation set
yolo task=detect mode=val \
    data=data/datasets/Fruit_dataset/data.yaml \
    model=data/models/yolov5n/Datasets\ YOLOv5n/runs/train/yolov5n_fruit_ripeness/weights/best.pt \
    imgsz=640

# Test on test set
yolo task=detect mode=val \
    data=data/datasets/Fruit_dataset/data.yaml \
    model=data/models/yolov5n/Datasets\ YOLOv5n/runs/train/yolov5n_fruit_ripeness/weights/best.pt \
    imgsz=640 \
    split=test
```

## 📖 API Usage

### Upload and Detect

**POST** `/api/detect`

Upload an image file to detect fruit ripeness.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `image` (image file)

**Response:**
```json
{
  "success": true,
  "scan_id": "uuid",
  "results": {
    "total_fruits": 3,
    "fruits": [
      {
        "type": "Fresh Banana",
        "confidence": 0.95,
        "quality_status": "fresh",
        "ripeness": "Unknown",
        "bbox": [x1, y1, x2, y2]
      }
    ],
    "fruit_counts": {
      "Fresh Banana": 2,
      "Ripe Mango": 1
    }
  }
}
```

### View Results

**GET** `/results/<scan_id>`

View detailed results page for a scan.

### Export Results

**GET** `/api/export/<scan_id>`

Export scan results as CSV.

## ⚙️ Configuration

Edit `config.py` to customize:

- **Model Path**: Trained YOLO model location
- **Dataset Path**: Dataset configuration file
- **Confidence Threshold**: Detection confidence (default: 0.25)
- **IOU Threshold**: Non-maximum suppression threshold (default: 0.45)
- **Database**: SQLite (default), PostgreSQL, or MySQL
- **NIR Scanner**: Enable/disable NIR integration

## 🗄️ Database

The application uses SQLite by default. Database file: `database/fruit_scanner.db`

To use PostgreSQL or MySQL, set environment variables in `.env`:
```
DATABASE_TYPE=postgresql
POSTGRESQL_HOST=localhost
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
```

## 📝 Notes

- Large folders (`data/`, `runs/`) are git-ignored
- Model weights (`.pt` files) are git-ignored - you'll need to train your own model or download pre-trained weights
- Database file (`database/fruit_scanner.db`) will be created automatically on first run
- Processed/uploaded images are git-ignored (user-generated content)
- Adjust `imgsz`, `batch`, and `epochs` based on hardware capabilities
- If `yolo` command is not found, use: `python -m ultralytics yolo ...`

## 🚨 Important for Deployment

This repository contains only the essential source code and configuration files needed to run the web scanner. The following are **NOT included** and must be set up separately:

- **Trained model weights** (`.pt` files) - Train your own model using the provided scripts or download pre-trained weights
- **Dataset files** - Add your own dataset following the structure in `docs/`
- **Database** - SQLite database will be created automatically on first run
- **User-generated images** - Processed and uploaded images are stored locally and not tracked

## 📚 Documentation

See `docs/` folder for detailed documentation:
- `API_DOCUMENTATION.md` - API reference
- `PHASE2_BACKEND.md` - Backend architecture
- `PHASE2_SUMMARY.md` - Project summary
- `README_SETUP.md` - Setup instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

[Add your license here]

## 👥 Authors

[Add author information here]
