# API Documentation - Fruit Quality Scanner

## Base URL

```
http://localhost:5000
```

## Endpoints

### 1. Home Page

**GET** `/`

Returns the main upload page.

**Response:** HTML page

---

### 2. Fruit Detection

**POST** `/api/detect`

Detect and analyze fruits in an uploaded image using YOLO and NIR fusion.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `image` (file, required): Image file (PNG, JPG, JPEG)

**Response (Success):**
```json
{
    "success": true,
    "scan_id": "550e8400-e29b-41d4-a716-446655440000",
    "results": {
        "scan_id": "550e8400-e29b-41d4-a716-446655440000",
        "image_path": "static/images/uploads/550e8400...jpg",
        "processed_image_path": "static/images/processed/550e8400...jpg",
        "results": [...],
        "total_fruits": 3,
        "fruits": [
            {
                "type": "Fresh Banana",
                "confidence": 0.85,
                "quality_status": "fresh",
                "ripeness": "Ripe",
                "yolo_confidence": 0.85,
                "nir_confidence": 0.80,
                "yolo_weight": 0.6,
                "nir_weight": 0.4,
                "fusion_method": "weighted_average",
                "bbox": [100, 150, 300, 400]
            }
        ],
        "fruit_counts": {
            "Fresh Banana": 2,
            "Ripe Mango": 1
        }
    }
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Error message here"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request (no file, invalid file type)
- `413` - File too large (>10MB)
- `500` - Server error

**Example (cURL):**
```bash
curl -X POST http://localhost:5000/api/detect \
  -F "image=@fruit_image.jpg"
```

---

### 3. View Results

**GET** `/results/<scan_id>`

Display the results page for a specific scan.

**Parameters:**
- `scan_id` (path parameter): UUID of the scan

**Response:** HTML page with:
- Annotated detection image
- Summary statistics
- Detailed results table
- Freshness analysis button

**Example:**
```
http://localhost:5000/results/550e8400-e29b-41d4-a716-446655440000
```

---

### 4. Export Results

**GET** `/api/export/<scan_id>`

Export scan results as CSV file.

**Parameters:**
- `scan_id` (path parameter): UUID of the scan

**Response:**
- Content-Type: `text/csv`
- File download: `fruit_scan_<scan_id>.csv`

**CSV Format:**
```csv
Fruit Type,Quality Status,Ripeness,Confidence (%)
Fresh Banana,fresh,Ripe,85.0
Ripe Mango,ripe,Ripe,78.5
```

**Status Codes:**
- `200` - Success
- `404` - Scan not found
- `500` - Server error

---

## Data Models

### Fruit Detection Result

```json
{
    "type": "Fresh Banana",
    "confidence": 0.85,
    "quality_status": "fresh",
    "ripeness": "Ripe",
    "yolo_confidence": 0.85,
    "nir_confidence": 0.80,
    "yolo_weight": 0.6,
    "nir_weight": 0.4,
    "fusion_method": "weighted_average",
    "bbox": [100, 150, 300, 400]
}
```

**Fields:**
- `type` (string): Fruit type/class name
- `confidence` (float): Final fused confidence (0-1)
- `quality_status` (string): fresh, ripe, unripe, overripe, rotten
- `ripeness` (string): Ripeness category
- `yolo_confidence` (float): YOLO detection confidence (0-1)
- `nir_confidence` (float): NIR/Felix confidence (0-1)
- `yolo_weight` (float): YOLO fusion weight (0.6)
- `nir_weight` (float): NIR fusion weight (0.4)
- `fusion_method` (string): Fusion method used
- `bbox` (array): Bounding box [x1, y1, x2, y2]

### Quality Status Values

- `fresh` - Fresh fruit
- `ripe` - Ripe fruit
- `unripe` - Unripe fruit
- `overripe` - Overripe fruit
- `rotten` - Rotten fruit

### Ripeness Values

- `Unripe`
- `Half-Ripe`
- `Ripe`
- `Overripe`

---

## Fusion Algorithm

The freshness score is computed using weighted averaging:

```
Freshness Score = (YOLO Confidence × 0.6) + (Felix/NIR Confidence × 0.4)
```

**Weights:**
- YOLO: 0.6 (60%)
- Felix/NIR: 0.4 (40%)

---

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

```json
{
    "success": false,
    "error": "Descriptive error message"
}
```

**Common Errors:**
- `No image file provided` - Missing image in request
- `Invalid file type` - Unsupported file format
- `File too large` - File exceeds 10MB limit
- `YOLO detector not initialized` - Model not loaded
- `Scan not found` - Invalid scan ID

---

## Rate Limiting

Currently no rate limiting implemented. Consider adding for production.

---

## Authentication

Currently no authentication required. Consider adding for production.

---

## CORS

CORS is enabled for all origins. Configure in production.

