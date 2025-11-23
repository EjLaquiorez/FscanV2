"""
Main Flask application for Fruit Quality Scanner
"""
import os
import uuid
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import json

from config import (
    UPLOAD_FOLDER, PROCESSED_FOLDER, MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS,
    MODEL_PATH, DATA_YAML_PATH, CONFIDENCE_THRESHOLD, IOU_THRESHOLD,
    NIR_ENABLED, NIR_MOCK_MODE, NIR_DEVICE_ID, NIR_API_URL,
    DATABASE_TYPE, DATABASE_URL
)

# Import modules
try:
    from models.yolo_detector import YOLODetector
    from models.fusion_engine import FusionEngine
    from nir.nir_scanner import create_nir_scanner
    from database.db_handler import DatabaseHandler
except ImportError as e:
    # Modules not yet created, will handle gracefully
    print(f"Warning: Could not import modules: {e}")
    YOLODetector = None
    FusionEngine = None
    create_nir_scanner = None
    DatabaseHandler = None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize components
yolo_detector = None
nir_scanner = None
fusion_engine = None
db_handler = None

def init_components():
    """Initialize YOLO, NIR, and database components"""
    global yolo_detector, nir_scanner, fusion_engine, db_handler
    
    try:
        if YOLODetector and MODEL_PATH.exists():
            yolo_detector = YOLODetector(str(MODEL_PATH), str(DATA_YAML_PATH))
            print("YOLO detector initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize YOLO detector: {e}")
    
    try:
        if create_nir_scanner:
            nir_scanner = create_nir_scanner()
            if nir_scanner:
                nir_scanner.connect()
                print("NIR scanner initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize NIR scanner: {e}")
        nir_scanner = None
    
    try:
        if YOLODetector and FusionEngine and yolo_detector and nir_scanner:
            fusion_engine = FusionEngine(yolo_detector, nir_scanner)
            print("Fusion engine initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize fusion engine: {e}")
        fusion_engine = None
    
    try:
        if DatabaseHandler:
            db_handler = DatabaseHandler()
            print("Database handler initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize database handler: {e}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/history')
def history():
    """History page showing past scans"""
    history_entries = []
    fruit_types = set()
    summary_stats = {
        'total_scans': 0,
        'total_fruits': 0,
        'latest_scan': None
    }

    def format_timestamp(ts: str) -> str:
        if not ts:
            return 'Unknown'
        try:
            dt = datetime.fromisoformat(ts)
            return dt.strftime('%b %d, %Y • %I:%M %p')
        except ValueError:
            return ts

    if db_handler:
        try:
            scans = db_handler.get_all_scans(limit=50)
            summary_stats['total_scans'] = len(scans)

            for scan in scans:
                scan_details = db_handler.get_scan(scan['scan_id'])
                if not scan_details:
                    continue

                timestamp = scan_details.get('timestamp')
                formatted_timestamp = format_timestamp(timestamp)
                fruits = scan_details.get('fruits', [])
                summary_stats['total_fruits'] += len(fruits)
                if not summary_stats['latest_scan']:
                    summary_stats['latest_scan'] = formatted_timestamp

                for fruit in fruits:
                    fruit_type = fruit.get('type', 'Unknown')
                    ripeness = fruit.get('ripeness', 'Unknown')
                    yolo_conf = fruit.get('yolo_confidence', fruit.get('confidence', 0)) or 0
                    nir_conf = fruit.get('nir_confidence', 0) or 0
                    freshness_score = (yolo_conf * 0.6 + nir_conf * 0.4) * 100

                    entry = {
                        'scan_id': scan_details.get('scan_id'),
                        'timestamp': formatted_timestamp,
                        'raw_timestamp': timestamp,
                        'fruit_type': fruit_type,
                        'ripeness': ripeness,
                        'quality_status': fruit.get('quality_status', 'Unknown'),
                        'freshness_score': freshness_score,
                        'yolo_confidence': yolo_conf * 100,
                        'nir_confidence': nir_conf * 100,
                        'confidence': (fruit.get('confidence', 0) or 0) * 100,
                        'total_fruits': len(fruits),
                        'status': 'Completed',
                        'processed_image_path': scan_details.get('processed_image_path')
                    }

                    history_entries.append(entry)
                    if fruit_type:
                        fruit_types.add(fruit_type)
        except Exception as e:
            print(f"Error loading history data: {e}")

    # Provide sample data if no history exists
    if not history_entries:
        sample_entries = [
            {
                'scan_id': 'demo-1',
                'timestamp': 'Nov 20, 2025 • 04:45 PM',
                'raw_timestamp': '2025-11-20T16:45:00',
                'fruit_type': 'Mango',
                'ripeness': 'Ripe',
                'quality_status': 'Fresh',
                'freshness_score': 92.5,
                'yolo_confidence': 95.0,
                'nir_confidence': 88.0,
                'confidence': 93.0,
                'total_fruits': 4,
                'status': 'Completed',
                'processed_image_path': None
            },
            {
                'scan_id': 'demo-2',
                'timestamp': 'Nov 19, 2025 • 10:12 AM',
                'raw_timestamp': '2025-11-19T10:12:00',
                'fruit_type': 'Pineapple',
                'ripeness': 'Unripe',
                'quality_status': 'Ripe',
                'freshness_score': 78.3,
                'yolo_confidence': 82.0,
                'nir_confidence': 72.0,
                'confidence': 80.0,
                'total_fruits': 3,
                'status': 'Exported',
                'processed_image_path': None
            }
        ]
        history_entries = sample_entries
        summary_stats['total_scans'] = len({entry['scan_id'] for entry in sample_entries})
        summary_stats['total_fruits'] = len(sample_entries)
        summary_stats['latest_scan'] = sample_entries[0]['timestamp']
        fruit_types = {entry['fruit_type'] for entry in sample_entries}

    fruit_types = sorted(list(fruit_types))

    return render_template(
        'history.html',
        history_entries=history_entries,
        summary_stats=summary_stats,
        fruit_types=fruit_types
    )

@app.route('/settings')
def settings():
    """Settings page showing configuration overview"""
    detection_settings = {
        'confidence_threshold': CONFIDENCE_THRESHOLD,
        'iou_threshold': IOU_THRESHOLD,
        'model_path': str(MODEL_PATH),
        'data_yaml_path': str(DATA_YAML_PATH),
        'max_upload_size_mb': round(MAX_UPLOAD_SIZE / (1024 * 1024), 1),
        'allowed_extensions': ', '.join(sorted(ext.upper() for ext in ALLOWED_EXTENSIONS))
    }

    nir_settings = {
        'enabled': NIR_ENABLED,
        'mock_mode': NIR_MOCK_MODE,
        'device_id': NIR_DEVICE_ID or 'Not configured',
        'api_url': NIR_API_URL or 'Not configured'
    }

    storage_settings = {
        'database_type': DATABASE_TYPE.title(),
        'database_url': DATABASE_URL,
        'upload_folder': str(UPLOAD_FOLDER),
        'processed_folder': str(PROCESSED_FOLDER)
    }

    system_status = {
        'yolo_detector': 'Connected' if yolo_detector else 'Not Initialized',
        'nir_scanner': 'Connected' if nir_scanner else 'Not Available',
        'fusion_engine': 'Ready' if fusion_engine else 'Offline',
        'database': 'Connected' if db_handler else 'Unavailable'
    }

    return render_template(
        'settings.html',
        detection_settings=detection_settings,
        nir_settings=nir_settings,
        storage_settings=storage_settings,
        system_status=system_status
    )

@app.route('/api/detect', methods=['POST'])
def detect():
    """API endpoint for fruit detection"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    
    try:
        # Ensure upload directory exists
        upload_dir = Path(app.config['UPLOAD_FOLDER'])
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        scan_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{scan_id}.{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        
        print(f"Saving uploaded file to: {filepath}")
        file.save(filepath)
        print(f"File saved successfully. Size: {os.path.getsize(filepath)} bytes")
        
        # Process image
        if not yolo_detector:
            error_msg = 'YOLO detector not initialized. Please check if the model file exists.'
            print(f"ERROR: {error_msg}")
            print(f"Model path: {MODEL_PATH}")
            print(f"Model exists: {MODEL_PATH.exists()}")
            return jsonify({'success': False, 'error': error_msg}), 500
        
        # Run YOLO detection
        print(f"Running YOLO detection on: {filepath}")
        yolo_results = yolo_detector.detect(filepath)
        print(f"YOLO detection completed. Found {len(yolo_results)} fruits.")
        
        # Use fusion engine if available, otherwise use YOLO only
        if fusion_engine and nir_scanner:
            try:
                print("Running fusion engine...")
                # Fuse YOLO and NIR results
                results = fusion_engine.fuse_detections(yolo_results, filepath)
                print(f"Fusion completed. {len(results)} fused results.")
            except Exception as e:
                import traceback
                print(f"Warning: Fusion failed, using YOLO only: {e}")
                print(f"Fusion traceback:\n{traceback.format_exc()}")
                results = yolo_results
        else:
            print("Fusion engine not available, using YOLO only.")
            results = yolo_results
        
        # Ensure processed directory exists
        processed_dir = Path(PROCESSED_FOLDER)
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Save processed image with annotations
        processed_filename = f"{scan_id}_processed.jpg"
        processed_path = os.path.join(str(PROCESSED_FOLDER), processed_filename)
        print(f"Saving annotated image to: {processed_path}")
        yolo_detector.save_annotated_image(filepath, processed_path, results)
        print("Annotated image saved successfully.")
        
        # Prepare results for database
        result_data = {
            'scan_id': scan_id,
            'image_path': filepath,
            'processed_image_path': processed_path,
            'results': results,
            'total_fruits': len(results),
            'fruits': []
        }
        
        # Count fruits by type and include fusion details
        fruit_counts = {}
        for result in results:
            # Use fruit_type (just fruit name) instead of class_name
            fruit_type = result.get('fruit_type', result.get('class_name', 'Unknown'))
            fruit_counts[fruit_type] = fruit_counts.get(fruit_type, 0) + 1
            result_data['fruits'].append({
                'type': fruit_type,  # Just the fruit name (e.g., "Pineapple", "Banana")
                'confidence': result.get('confidence', 0),
                'quality_status': result.get('quality_status', 'Unknown'),  # unripe, ripe, overripe
                'ripeness': result.get('ripeness', 'Unknown'),  # Unripe, Ripe, Overripe
                'yolo_confidence': result.get('yolo_confidence', result.get('confidence', 0)),
                'nir_confidence': result.get('nir_confidence', 0),
                'yolo_weight': 0.6,
                'nir_weight': 0.4,
                'fusion_method': result.get('fusion_method', 'weighted_average'),
                'bbox': result.get('bbox', [])
            })
        
        result_data['fruit_counts'] = fruit_counts
        
        # Save to database
        if db_handler:
            try:
                db_handler.save_scan(scan_id, filepath, processed_path, result_data)
            except Exception as e:
                print(f"Warning: Could not save to database: {e}")
        
        return jsonify({
            'success': True,
            'scan_id': scan_id,
            'results': result_data
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in detection: {e}")
        print(f"Full traceback:\n{error_trace}")
        
        # Return detailed error in debug mode, generic in production
        if app.config.get('DEBUG', False):
            return jsonify({
                'success': False, 
                'error': str(e),
                'traceback': error_trace
            }), 500
        else:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/results/<scan_id>')
def results(scan_id):
    """Display results page"""
    try:
        # Load results from database or file
        if db_handler:
            scan_data = db_handler.get_scan(scan_id)
            if scan_data:
                results_data = scan_data.get('results', {})
                fruits = results_data.get('fruits', [])
                
                # Calculate statistics based on quality_status/ripeness, not fruit type
                total_fruits = len(fruits)
                fresh_count = sum(1 for f in fruits if f.get('quality_status', '').lower() == 'fresh')
                ripe_count = sum(1 for f in fruits if f.get('ripeness', '').lower() == 'ripe')
                unripe_count = sum(1 for f in fruits if f.get('ripeness', '').lower() == 'unripe')
                
                # Get processed image path
                result_image = f"/static/images/processed/{scan_id}_processed.jpg"
                
                return render_template('results.html',
                    result_image=result_image,
                    fruits=fruits,
                    total_fruits=total_fruits,
                    fresh_count=fresh_count,
                    ripe_count=ripe_count,
                    unripe_count=unripe_count
                )
        
        # Fallback if database not available
        return render_template('results.html',
            result_image="/static/images/placeholder.jpg",
            fruits=[],
            total_fruits=0,
            fresh_count=0,
            ripe_count=0,
            unripe_count=0
        )
    
    except Exception as e:
        print(f"Error loading results: {e}")
        return redirect(url_for('index'))

@app.route('/api/export/<scan_id>')
def export_results(scan_id):
    """Export results as CSV"""
    try:
        if db_handler:
            scan_data = db_handler.get_scan(scan_id)
            if scan_data:
                results_data = scan_data.get('results', {})
                fruits = results_data.get('fruits', [])
                
                # Generate CSV
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['Fruit Type', 'Quality Status', 'Ripeness', 'Confidence (%)'])
                
                for fruit in fruits:
                    writer.writerow([
                        fruit.get('type', 'Unknown'),
                        fruit.get('quality_status', 'Unknown'),
                        fruit.get('ripeness', 'Unknown'),
                        f"{fruit.get('confidence', 0) * 100:.1f}"
                    ])
                
                output.seek(0)
                return send_file(
                    io.BytesIO(output.getvalue().encode()),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f'fruit_scan_{scan_id}.csv'
                )
        
        return jsonify({'error': 'Results not found'}), 404
    
    except Exception as e:
        print(f"Error exporting results: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'success': False, 'error': 'File too large. Maximum size is 10MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize components on startup
    print("\n" + "=" * 60)
    print("Initializing Fruit Quality Scanner...")
    print("=" * 60)
    init_components()
    print("=" * 60 + "\n")
    
    # Run the app
    from config import HOST, PORT, DEBUG
    print(f"Starting Flask server on {HOST}:{PORT}")
    print(f"Debug mode: {DEBUG}")
    print(f"Access the application at: http://localhost:{PORT}\n")
    app.run(host=HOST, port=PORT, debug=DEBUG)

