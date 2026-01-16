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

### Supported Classes (15 classes)

**Banana:**
- Banana Unripe
- Banana Ripe
- Banana Overripe

**Mango:**
- Mango Unripe
- Mango Ripe
- Mango Overripe

**Cashew:**
- Cashew Unripe
- Cashew Ripe
- Cashew Overripe

**Cacao:**
- Cacao Unripe
- Cacao Ripe
- Cacao Overripe

**Pineapple:**
- Pineapple Unripe
- Pineapple Ripe
- Pineapple Overripe

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

## 🏗️ Architecture & Classes

### Core Classes

#### `YOLODetector` (`models/yolo_detector.py`)
YOLO-based fruit detection engine using Ultralytics YOLOv5n model.

**Initialization:**
```python
detector = YOLODetector(
    model_path: str,
    data_yaml_path: str,
    confidence_threshold: float = 0.25,
    iou_threshold: float = 0.45
)
```

**Key Methods:**
- `detect(image_path: str) -> List[Dict]` - Detect fruits in an image, returns list of detections with bounding boxes, classes, and confidence scores
- `save_annotated_image(input_path: str, output_path: str, detections: List[Dict]) -> None` - Save image with bounding box annotations
- `get_class_names() -> Dict[int, str]` - Get dictionary of class ID to class name mappings

**Detection Result Format:**
```python
{
    'bbox': [x1, y1, x2, y2],
    'class_id': int,
    'class_name': str,  # e.g., "Banana Unripe", "Mango Ripe"
    'fruit_type': str,  # e.g., "Banana", "Mango" (ripeness removed)
    'confidence': float,
    'quality_status': str,  # 'unripe', 'ripe', 'overripe', 'fresh', 'rotten'
    'ripeness': str  # 'Unripe', 'Ripe', 'Overripe', 'Half-Ripe'
}
```

**Supported Classes (15 classes):**
- Banana: Unripe, Ripe, Overripe
- Mango: Unripe, Ripe, Overripe
- Cashew: Unripe, Ripe, Overripe
- Cacao: Unripe, Ripe, Overripe
- Pineapple: Unripe, Ripe, Overripe

---

#### `FusionEngine` (`models/fusion_engine.py`)
Fuses YOLO detection results with NIR (Near-Infrared) analysis for enhanced quality assessment.

**Initialization:**
```python
fusion_engine = FusionEngine(
    yolo_detector: YOLODetector,
    nir_scanner: NIRScannerBase
)
```

**Key Methods:**
- `fuse_detections(yolo_results: List[Dict], image_path: str) -> List[Dict]` - Fuse YOLO and NIR results for each detection
- `set_fusion_weights(yolo_weight: float, nir_weight: float)` - Adjust fusion weights (default: YOLO=0.7, NIR=0.3)

**Fusion Strategy:**
- Weighted average: YOLO (70%) + NIR (30%)
- Agreement checking: If YOLO and NIR agree on ripeness, confidence is boosted
- Disagreement handling: Uses weighted decision based on confidence scores

**Fused Result Format:**
```python
{
    'bbox': [x1, y1, x2, y2],
    'class_id': int,
    'class_name': str,
    'confidence': float,  # Overall fused confidence
    'yolo_confidence': float,
    'nir_confidence': float,
    'quality_status': str,
    'ripeness': str,
    'yolo_ripeness': str,
    'nir_ripeness': str,
    'ripeness_confidence': float,
    'nir_quality_score': float,
    'fusion_method': str,  # 'weighted_average'
    'agreement': str  # 'high' or 'moderate'
}
```

---

#### `NIRScannerBase` (`nir/nir_scanner.py`)
Abstract base class for NIR scanner implementations.

**Abstract Methods:**
- `connect() -> bool` - Connect to NIR scanner device
- `disconnect() -> None` - Disconnect from device
- `scan(region: Optional[Tuple[int, int, int, int]] = None) -> Dict` - Perform NIR scan on region
- `get_spectral_data() -> np.ndarray` - Get raw spectral data from last scan
- `analyze_ripeness(spectral_data: Optional[np.ndarray] = None) -> Dict` - Analyze ripeness from spectral data

**Scan Result Format:**
```python
{
    'spectral_data': List[float],
    'wavelengths': List[float],
    'analysis': {
        'ripeness_score': float,  # 0-1
        'ripeness_category': str,  # 'Unripe', 'Half-Ripe', 'Ripe', 'Overripe'
        'quality_score': float,  # 0-1
        'sugar_content': float,  # %
        'moisture_content': float,  # %
        'mean_reflectance': float,
        'std_reflectance': float,
        'confidence': float
    },
    'region': Tuple[int, int, int, int]  # Optional bounding box
}
```

#### `MockNIRScanner` (`nir/nir_scanner.py`)
Mock implementation of NIR scanner for development and testing. Generates simulated spectral data and analysis results.

#### `RealNIRScanner` (`nir/nir_scanner.py`)
Placeholder for real NIR scanner hardware integration. Currently not implemented.

**Factory Function:**
```python
nir_scanner = create_nir_scanner() -> NIRScannerBase
```
Returns `MockNIRScanner` or `RealNIRScanner` based on configuration.

---

#### `DatabaseHandler` (`database/db_handler.py`)
Database operations handler supporting SQLite, PostgreSQL, and MySQL.

**Initialization:**
```python
db_handler = DatabaseHandler(database_url: Optional[str] = None)
```

**Key Methods:**
- `save_scan(scan_id: str, image_path: str, processed_image_path: str, results_data: Dict) -> bool` - Save scan results
- `get_scan(scan_id: str) -> Optional[Dict]` - Retrieve scan data by ID
- `get_all_scans(limit: int = 100, offset: int = 0) -> List[Dict]` - Get paginated list of scans
- `delete_scan(scan_id: str) -> bool` - Delete scan from database
- `get_statistics() -> Dict` - Get database statistics (total scans, fruits, counts by type/quality)
- `clear_all_scans() -> bool` - Clear all scan history

**Database Models:**

**`Scan` Table:**
- `id` (String, Primary Key) - Scan ID (UUID)
- `timestamp` (DateTime) - Scan timestamp
- `image_path` (String) - Path to original image
- `processed_image_path` (String) - Path to annotated image
- `results_json` (JSON) - Full results as JSON
- `total_fruits` (Integer) - Number of fruits detected
- `created_at` (DateTime) - Record creation time

**`Fruit` Table:**
- `id` (Integer, Primary Key) - Auto-increment ID
- `scan_id` (String, Foreign Key) - Reference to Scan
- `fruit_type` (String) - Fruit name (e.g., "Banana", "Mango")
- `class_id` (Integer) - YOLO class ID
- `class_name` (String) - Full class name (e.g., "Banana Unripe")
- `quality_status` (String) - Quality status (unripe, ripe, overripe, fresh, rotten)
- `ripeness` (String) - Ripeness level (Unripe, Ripe, Overripe, Half-Ripe)
- `confidence` (Float) - Overall confidence score
- `yolo_confidence` (Float) - YOLO detection confidence
- `nir_confidence` (Float) - NIR analysis confidence
- `bbox_x1, bbox_y1, bbox_x2, bbox_y2` (Float) - Bounding box coordinates
- `nir_quality_score` (Float) - NIR quality assessment score
- `fusion_method` (String) - Fusion method used
- `created_at` (DateTime) - Record creation time

---

### Class Relationships

```
Flask App (app.py)
    ├── YOLODetector ──┐
    │                  ├──> FusionEngine
    └── NIRScannerBase ┘
    │
    └── DatabaseHandler
            ├── Scan (SQLAlchemy Model)
            └── Fruit (SQLAlchemy Model)
```

**Data Flow:**
1. User uploads image → Flask app receives request
2. `YOLODetector.detect()` → Detects fruits using YOLO model
3. `FusionEngine.fuse_detections()` → Combines YOLO + NIR results (if NIR enabled)
4. `DatabaseHandler.save_scan()` → Stores results in database
5. Results returned to user via API response

---

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
