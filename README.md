# FscanV2 — Fruit Quality Scanner

A fruit ripeness detection web application built around a **FELIX-inspired bimodal framework** at **Technology Readiness Level 3 (TRL 3)**.

- **Visual modality:** Ultralytics YOLO detection (e.g. YOLOv5n / class set in `data.yaml`; `requirements.txt` pins the `ultralytics` train/infer stack).
- **Chemical modality (simulated):** No physical gas or NIR hardware in this build. The app uses a **mathematical chemical simulator** (ethylene dynamics \(E(t)=E_0 e^{kt}\), environmental drift, and NIR-style proxy signals) described in `models/chemical_simulator.py`.
- **Fusion:** **Late fusion** at decision level—default weights **0.7 visual / 0.3 chemical**, with **conflict resolution** when visual confidence and the normalized chemical proxy disagree beyond a threshold \(\delta\) (see `models/fusion_engine.py` and the Settings page).

**Important:** All chemical sensing outputs are **simulated**. The UI and API may still expose a field named `nir_confidence` for compatibility; in the TRL 3 pipeline it carries the **normalized chemical proxy** \(\hat{E}(t)\in[0,1]\), not data from a real spectrometer.

---

## TRL 3 implementation snapshot

| Area | Location / behavior |
|------|---------------------|
| Flask app, detect pipeline, TRL disclaimer in API | `app.py` |
| Inline app config (paths, simulation, fusion, freshness thresholds) | `Config` in `app.py` |
| Shared env / DB URL / simulation constants for DB layer | `config.py` |
| Chemical simulation (`ChemicalSimulator`, `ChemicalReading`) | `models/chemical_simulator.py` |
| Late fusion + batch fuse + freshness labels | `models/fusion_engine.py` |
| Bootstrap CI, McNemar (thesis-style validation helpers) | `utils/statistical_validator.py` *(uses `scikit-learn`, pinned in `requirements.txt`)* |
| Per-class performance charts from training outputs | `scripts/generate_per_class_performance.py` |

Detection flow: upload → YOLO → per-detection chemical readings → `FusionEngine.batch_fuse` → annotated image + JSON (including `chemical_data`, `fusion_details`, `simulation_metadata`, `trl_disclaimer`).

---

## 📁 Repository Structure

```
FscanV2/
├── app.py                 # Main Flask app (TRL 3 bimodal pipeline)
├── config.py              # Environment, DB URL, TRL simulation constants
├── requirements.txt       # Python dependencies
│
├── docs/                  # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── PHASE2_BACKEND.md
│   ├── PHASE2_SUMMARY.md
│   └── README_SETUP.md
│
├── scripts/               # Utility scripts
│   ├── auto_label_dataset.py
│   ├── train_yolov5.py
│   ├── generate_per_class_performance.py  # Per-class metrics charts
│   ├── generate_fusion_diagram.py
│   ├── generate_confidence_comparison_graph.py
│   ├── generate_response_time_graph.py
│   ├── run_app.bat
│   ├── run_app.ps1
│   └── optimize_gpu_performance.bat
│
├── data/                  # Data and models (often git-ignored)
│   ├── datasets/Fruit_dataset/
│   └── models/yolov5n/runs/...
│
├── models/                # Application logic (not only weights)
│   ├── yolo_detector.py
│   ├── chemical_simulator.py   # TRL 3 synthetic chemical / proxy signals
│   └── fusion_engine.py        # Late fusion + conflict handling
│
├── utils/
│   └── statistical_validator.py
│
├── database/
│   └── db_handler.py
│
├── nir/                   # Optional NIR scanner abstractions (mock/real stubs)
│   └── nir_scanner.py
│
├── static/                # css/, js/, images/
├── templates/             # index, results, history, settings, ...
└── tests/                 # pytest suite
    ├── conftest.py
    ├── test_app_helpers.py
    ├── test_app_routes.py
    ├── test_chemical_simulator.py
    └── test_fusion_engine.py
```

**Weights and dataset YAML:** The running app resolves paths in `Config` inside `app.py`:

| Override (optional) | Purpose |
|---------------------|--------|
| `YOLO_MODEL_PATH` | Absolute path to a `.pt` checkpoint |
| `YOLO_DATA_YAML` | Absolute path to `data.yaml` |

If those are unset, the first **existing** file wins, in order:

- **Model:** `models/weights/best.pt` → `data/models/yolov5n/runs/train/yolov5n_fruit_ripeness/weights/best.pt`
- **YAML:** repo-root `data.yaml` → `data/datasets/Fruit_dataset/data.yaml`

`config.py` still defines default `MODEL_PATH` / `DATA_YAML_PATH` for the database layer and tooling; keep training outputs or env vars aligned with what `app.py` resolves.

**Uploads (Flask):** Original uploads are stored under `uploads/` at the repository root (`Config.UPLOAD_FOLDER` in `app.py`), not under `static/images/uploads` (which `config.py` uses for some legacy paths).

---

## 🚀 Quick Start

### 1. Environment Setup

```powershell
cd "path\to\FscanV2"

# Create and activate virtual environment (name can be .venv or .venv_yolo)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

# Optional: CUDA PyTorch
# pip install --index-url https://download.pytorch.org/whl/cu121 torch torchvision torchaudio
```

**Dependency notes**

- **SQLAlchemy:** `requirements.txt` pins `sqlalchemy>=2.0.36` because older 2.0.x releases fail on **Python 3.14+** during import.
- **PostgreSQL:** the project uses **`psycopg` v3** (`psycopg[binary]` in `requirements.txt`), which ships wheels for recent Python versions including **3.14**. The DB URL uses the `postgresql+psycopg://` dialect in `config.py`. Default `DATABASE_TYPE` is still **sqlite** for local runs.
- **Statistical utilities:** `scikit-learn` is listed in `requirements.txt` for `utils/statistical_validator.py` and general scientific stack compatibility; the main `/api/detect` path does not require calling that module.

The legacy script `scripts/run_app.ps1` looks for a venv named **`.venv_yolo`**. Either create/rename your venv to match or run `python app.py` from an activated `.venv` as above.

### 2. Run the Application

**Option A: PowerShell / batch scripts** (expects `.venv_yolo` unless you edit the script)

```powershell
.\scripts\run_app.ps1
# or
.\scripts\run_app.bat
```

**Option B: Direct Python (after activating `.venv`)**

```powershell
python app.py
```

The application listens on **`http://localhost:5000`** (and `0.0.0.0:5000` if configured).

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

### Per-class performance charts

`scripts/generate_per_class_performance.py` builds a **per-class performance figure** (precision, recall, mAP@0.5, F1) and saves it under `docs/` (default output: `docs/yolo_per_class_performance.png`). It looks for training artifacts under `data/models/yolov5/runs/train/` when present; otherwise it synthesizes illustrative metrics for the chart. **pandas** and **PyYAML** improve result parsing if installed.

```powershell
python scripts/generate_per_class_performance.py
```

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

### Automated tests (pytest)

From the repository root (with the virtual environment activated):

```powershell
pytest tests/ -q
```

### YOLO validation / val split

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

### Upload and Detect (TRL 3 bimodal)

**POST** `/api/detect`

Upload an image for **YOLO detection + simulated chemical readings + late fusion**.

**Request** (`multipart/form-data`):

| Field | Description |
|--------|-------------|
| `image` | Image file (required) |
| `hours_since_harvest` | Optional; default **24** (hours). Drives ethylene simulation. |
| `temperature` | Optional; °C, default from app simulation settings (typically **25**). |
| `humidity` | Optional; relative humidity %, default **80**. |

**Response** (success): `results` includes, among other fields:

- `trl_disclaimer` — TRL 3 / simulation disclaimer text.
- `simulation_metadata` — ethylene model string, noise \(\sigma\), fusion weights, classification thresholds, and the temperature/humidity/hours used.
- `fruits` — list of detections with:
  - `type`, `ripeness` (fusion-based label: **Unripe / Ripe / Overripe** per `FRESHNESS_THRESHOLDS`; high fusion score → Unripe), `confidence` (fusion score), `yolo_confidence`
  - `nir_confidence` — **normalized chemical proxy** \(\hat{E}(t)\in[0,1]\) (name kept for API compatibility)
  - `chemical_data` — `ethylene_ppm`, `brix`, `moisture`, `composite_quality`
  - `fusion_details` — `has_conflict`, `disagreement`, `resolution_strategy`, `weights`
  - `bbox`
- `statistics` — batch fusion summaries when the fusion engine is active

Example (trimmed):

```json
{
  "success": true,
  "scan_id": "uuid",
  "results": {
    "trl_disclaimer": "...",
    "simulation_metadata": { "ethylene_model": "E(t) = E₀e^(kt)", "input_conditions": { } },
    "total_fruits": 2,
    "fruits": [
      {
        "type": "Banana",
        "ripeness": "Ripe",
        "confidence": 0.82,
        "yolo_confidence": 0.91,
        "nir_confidence": 0.61,
        "chemical_data": {
          "ethylene_ppm": 1.2,
          "brix": 14.5,
          "moisture": 82.0,
          "composite_quality": 0.71
        },
        "fusion_details": {
          "has_conflict": false,
          "resolution_strategy": "standard_fusion",
          "weights": { "alpha_visual": 0.7, "beta_chemical": 0.3 }
        },
        "bbox": [x1, y1, x2, y2]
      }
    ],
    "statistics": { }
  }
}
```

### View Results

**GET** `/results/<scan_id>`

View detailed results page for a scan.

### Export Results

**GET** `/api/export/<scan_id>`

Export individual scan results as a formatted text file (.txt). The report includes:
- Scan information (ID, date, total fruits)
- Ripeness summary statistics
- Detailed detection results grouped by fruit type
- Confidence scores (overall, YOLO, and **chemical proxy** — may be labeled “NIR” in older exports)

**GET** `/api/export-history`

Export all scan history as CSV file. Includes all scans with columns:
- Scan ID, Timestamp, Total Fruits
- Fruit Type, Ripeness, Confidence scores
- YOLO and chemical-proxy columns (historically named for NIR in some views)

Useful for bulk data analysis in Excel or other spreadsheet applications.

## ⚙️ Configuration

- **Detection & TRL 3 fusion (primary):** The running Flask app reads **`Config` inside `app.py`** for model paths, upload limits, simulation parameters (`SIMULATION_PARAMS`), late fusion weights (`FUSION_WEIGHTS`), and freshness thresholds (`FRESHNESS_THRESHOLDS`). Adjust there for behavior you see in `/settings` and `/api/detect`.

- **`config.py`:** Database URL (`DATABASE_TYPE`, SQLite path, PostgreSQL/MySQL env vars), directory creation, and mirrored simulation/fusion constants used by the **database** layer and shared tooling. Keep DB-related values here in sync with deployment.

- **Legacy / optional NIR package:** `nir/nir_scanner.py` and NIR flags in `config.py` support earlier mock-hardware stories; the **current default pipeline** in `app.py` uses **`ChemicalSimulator` + `FusionEngine`**, not live NIR fusion.

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
**Late fusion** between **YOLO confidence** \(C_{\text{YOLO}}\) and the **normalized chemical proxy** \(\hat{E}(t)\) from `ChemicalSimulator` (thesis-style weights \(\alpha=0.7\), \(\beta=0.3\), conflict threshold \(\delta \approx 0.15\)).

**Initialization:**
```python
fusion_engine = FusionEngine(alpha=0.7, beta=0.3, delta=0.15)
```

**Key Methods:**
- `fuse_single(c_yolo, e_hat, fruit_type='unknown') -> Dict` — single detection; returns `fusion_score`, `classification` (**Unripe / Ripe / Overripe** from \(F(t)\) vs `FRESHNESS_THRESHOLDS`), conflict flags, and resolution strategy.
- `batch_fuse(yolo_prepared, chemical_readings) -> List[Dict]` — aligns each YOLO box with a `ChemicalReading` or dict with `normalized_proxy`.

**Conflict handling (summary):** If \(|C_{\text{YOLO}} - \hat{E}(t)| > \delta\), weights shift to **(0.9, 0.1)** when YOLO is higher (`resolution_strategy`: `yolo_dominant`) or **(0.6, 0.4)** when the proxy is higher (`chemical_boosted`); otherwise **standard** \( \alpha C_{\text{YOLO}} + \beta \hat{E}(t)\) with `resolution_strategy`: `standard_fusion`.

**Fused result fields (typical):** `fusion_score`, `classification`, `visual_confidence`, `chemical_proxy`, `has_conflict`, `disagreement`, `resolution_strategy`, `weights_applied` (and `resolution_note`), plus bbox / class passthrough from the batch step.

---

#### `ChemicalSimulator` (`models/chemical_simulator.py`)
Generates **synthetic** ethylene and NIR-proxy features per fruit type (climacteric parameters, caps, noise, temperature/humidity drift). Exposes `simulate(...)` → `ChemicalReading` and `batch_simulate` for multiple detections.

---

#### `StatisticalValidator` (`utils/statistical_validator.py`)
Helpers for **bootstrap confidence intervals** and **McNemar’s test** (paired YOLO vs fusion). **`scikit-learn`** is included in `requirements.txt` for this and other dependencies.

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
    ├── YOLODetector
    ├── ChemicalSimulator  ──┐
    │                         ├──> FusionEngine.batch_fuse(...)
    └── (optional StatisticalValidator for offline analysis)
    │
    └── DatabaseHandler
            ├── Scan (SQLAlchemy Model)
            └── Fruit (SQLAlchemy Model)
```

**Data Flow (TRL 3):**
1. Upload image → save under configured upload folder
2. `YOLODetector.detect()` → bounding boxes and class names
3. `ChemicalSimulator.simulate()` per detection (fruit type, hours, temp, humidity)
4. `FusionEngine.batch_fuse()` → fused freshness label and scores
5. `DatabaseHandler.save_scan()` → persist JSON results (when DB available)
6. API returns structured results + simulation metadata + disclaimer

---

## 📊 Performance Analysis

The simulated response time results suggest that the bimodal framework incurs additional computational overhead due to feature fusion. Nevertheless, the projected response time remains within acceptable limits based on simulation assumptions, indicating potential feasibility for real-time implementation.

![Projected Response Time Comparison](docs/response_time_comparison.png)

While the bimodal framework requires more processing time, it demonstrates superior accuracy in freshness detection. The fusion of visual and chemical features results in significantly higher confidence scores compared to using either modality independently.

![Freshness Confidence Comparison](docs/confidence_comparison.png)

---

## 🔬 Fusion Formulation

**Implementation note:** In `models/fusion_engine.py`, the live pipeline computes one fused score \(F(t)\) with optional **conflict weighting**, then assigns **Unripe / Ripe / Overripe** using scalar thresholds (`FRESHNESS_THRESHOLDS` in `config.py` / `app.py`). The multi-stage **\(R_{\text{YOLO}}\) vs \(R_{\text{NIR}}\)** agreement rules in this section follow the **thesis / diagram** narrative; they are **not** spelled out as separate stages in the current engine.

The bimodal fusion framework combines **visual (YOLO)** and a **chemical proxy** (simulated \(\hat{E}(t)\) standing in for thesis NIR / FELIX-style sensing). The diagrams and algebra below were written with **NIR** notation; in the **current codebase**, treat **\(C_{\text{NIR}}\)** as **the normalized chemical proxy** from `ChemicalSimulator`, not laboratory spectra.

![Fusion Formulation Diagram](docs/fusion_formulation_diagram.png)

### Overall Confidence Fusion

The overall confidence score is computed using a weighted average of YOLO and NIR confidence scores:

\[
C_{overall} = w_{YOLO} \cdot C_{YOLO} + w_{NIR} \cdot C_{NIR}
\]

Where:
- \(C_{overall}\) = Overall fused confidence score
- \(C_{YOLO}\) = YOLO detection confidence (0-1)
- \(C_{NIR}\) = NIR analysis confidence (0-1)
- \(w_{YOLO} = 0.7\) = Weight for YOLO modality
- \(w_{NIR} = 0.3\) = Weight for NIR modality
- Constraint: \(w_{YOLO} + w_{NIR} = 1.0\)

### Ripeness Classification Fusion

The final ripeness classification is determined through a multi-stage decision process:

#### Stage 1: Agreement Check

First, the system checks if YOLO and NIR agree on the ripeness category:

\[
\text{Agreement} = \begin{cases}
\text{True} & \text{if } R_{YOLO} = R_{NIR} \text{ or } |\text{Index}(R_{YOLO}) - \text{Index}(R_{NIR})| \leq 1 \\
\text{False} & \text{otherwise}
\end{cases}
\]

Where:
- \(R_{YOLO}\) = YOLO ripeness category: {Unripe, Half-Ripe, Ripe, Overripe}
- \(R_{NIR}\) = NIR ripeness category: {Unripe, Half-Ripe, Ripe, Overripe}
- \(\text{Index}(\cdot)\) = Position in ordered set: Unripe=0, Half-Ripe=1, Ripe=2, Overripe=3

#### Stage 2: Final Ripeness Decision

The final ripeness classification follows these rules:

**Case 1: High Agreement**
\[
R_{final} = R_{YOLO}
\]
\[
C_{ripeness} = \min\left(1.0, \frac{C_{YOLO} + C_{NIR}}{2} + 0.1\right)
\]

When both modalities agree, the confidence is boosted by 0.1.

**Case 2: YOLO High Confidence**
\[
\text{If } C_{YOLO} \geq 0.8: \quad R_{final} = R_{YOLO}, \quad C_{ripeness} = C_{YOLO}
\]

**Case 3: Disagreement with Weighted Decision**
\[
R_{final} = \begin{cases}
R_{YOLO} & \text{if } C_{YOLO} > C_{NIR} + 0.2 \text{ or } C_{YOLO} \geq 0.7 \\
R_{NIR} & \text{if } C_{NIR} > C_{YOLO} + 0.2 \\
R_{YOLO} & \text{if } w_{YOLO} \cdot C_{YOLO} \geq w_{NIR} \cdot C_{NIR} \\
R_{NIR} & \text{otherwise}
\end{cases}
\]
\[
C_{ripeness} = \frac{C_{YOLO} + C_{NIR}}{2}
\]

### Feature Fusion Summary

The complete fusion process can be summarized as:

\[
\text{Fused Result} = \begin{cases}
\text{bbox} & = \text{YOLO bounding box} \\
\text{class\_id} & = \text{YOLO class ID} \\
\text{class\_name} & = \text{YOLO class name} \\
\text{confidence} & = w_{YOLO} \cdot C_{YOLO} + w_{NIR} \cdot C_{NIR} \\
\text{ripeness} & = f(R_{YOLO}, R_{NIR}, C_{YOLO}, C_{NIR}) \\
\text{ripeness\_confidence} & = g(\text{Agreement}, C_{YOLO}, C_{NIR}) \\
\text{quality\_score} & = \text{NIR quality score}
\end{cases}
\]

Where \(f(\cdot)\) and \(g(\cdot)\) represent the decision functions described in Stage 2.

### Advantages of Bimodal Fusion

1. **Robustness**: Combining two independent modalities reduces false positives and improves accuracy
2. **Confidence Boost**: Agreement between modalities increases overall confidence
3. **Adaptive Weighting**: The system adapts to modality reliability through confidence-based decisions
4. **Quality Assessment**: NIR provides additional quality metrics (sugar content, moisture) beyond visual appearance

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
