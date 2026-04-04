"""
Main Flask application for Fruit Freshness Detection
FELIX-Inspired Bimodal Framework - Technology Readiness Level 3 (Simulation Only)

This application implements:
- YOLOv5-Nano for visual detection (validated component)
- Mathematical simulation of chemical sensing (E(t) = E₀e^(kt))
- Late Fusion (0.7 visual / 0.3 chemical) with conflict resolution
- Statistical validation (Bootstrap CI, McNemar's test)
- Sensitivity analysis (±20% parameter variation)

DISCLAIMER: This is TRL 3 (Experimental Proof of Concept). 
All chemical sensing data is mathematically simulated.
Hardware validation required at TRL 4-5 before deployment.
"""

import os
import uuid
import re
import json
import traceback
import io
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

import numpy as np
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename


def _resolve_yolo_model_path(base: Path) -> Path:
    """Prefer YOLO_MODEL_PATH env, then first existing weights file under the repo."""
    env = os.getenv('YOLO_MODEL_PATH')
    if env:
        p = Path(env)
        if p.is_file():
            return p
    candidates = [
        base / 'models' / 'weights' / 'best.pt',
        base / 'data' / 'models' / 'yolov5n' / 'runs' / 'train' / 'yolov5n_fruit_ripeness' / 'weights' / 'best.pt',
    ]
    for c in candidates:
        if c.is_file():
            return c
    return candidates[0]


def _resolve_data_yaml_path(base: Path) -> Path:
    env = os.getenv('YOLO_DATA_YAML')
    if env:
        p = Path(env)
        if p.is_file():
            return p
    candidates = [
        base / 'data.yaml',
        base / 'data' / 'datasets' / 'Fruit_dataset' / 'data.yaml',
    ]
    for c in candidates:
        if c.is_file():
            return c
    return candidates[0]


# Configuration
class Config:
    # Paths
    BASE_DIR = Path(__file__).parent
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    PROCESSED_FOLDER = BASE_DIR / 'static' / 'images' / 'processed'
    TEMPLATES_DIR = BASE_DIR / 'templates'
    STATIC_DIR = BASE_DIR / 'static'
    
    # Model settings (env YOLO_MODEL_PATH / YOLO_DATA_YAML override; else first existing path)
    MODEL_PATH = _resolve_yolo_model_path(BASE_DIR)
    DATA_YAML_PATH = _resolve_data_yaml_path(BASE_DIR)
    
    # Detection settings
    CONFIDENCE_THRESHOLD = 0.25
    IOU_THRESHOLD = 0.45
    MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
    
    # Allowed extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    
    # TRL 3 Simulation Parameters (Thesis Section 3.2, 3.3)
    SIMULATION_PARAMS = {
        'ethylene_noise_sigma': 0.05,      # Gaussian σ = 0.05 (Voss et al.)
        'temperature_coefficient': 0.15,    # β = ±15%
        'humidity_coefficient': 0.05,       # γ = 0.05
        'nominal_temperature': 25,          # 25°C baseline
        'nominal_humidity': 80,             # 80% RH baseline
        'conflict_threshold': 0.15          # δ = 0.15 (Section 3.3.5)
    }
    
    # Late Fusion Weights (Thesis Section 3.3.3 - validated by ablation)
    FUSION_WEIGHTS = {
        'alpha_visual': 0.7,           # YOLO weight
        'beta_chemical': 0.3,          # Chemical proxy weight
        'conflict_yolo_boost': 0.9,    # When YOLO >> Chemical
        'conflict_chem_boost': 0.4     # When Chemical >> YOLO
    }
    
    # Classification Thresholds (Thesis Table 3.3.4)
    FRESHNESS_THRESHOLDS = {
        'fresh': 0.80,      # F(t) >= 0.80
        'ripe': 0.65,       # 0.65 <= F(t) < 0.80
        'overripe': 0.00    # F(t) < 0.65
    }
    
    # Flask settings
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'trl3-simulation-secret-key')

config = Config()

# Initialize Flask
app = Flask(__name__, 
            template_folder=str(config.TEMPLATES_DIR),
            static_folder=str(config.STATIC_DIR))
app.config['UPLOAD_FOLDER'] = str(config.UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_UPLOAD_SIZE
app.config['SECRET_KEY'] = config.SECRET_KEY

# Ensure directories exist
config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
config.PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

# Global component instances
yolo_detector = None
chemical_simulator = None
fusion_engine = None
statistical_validator = None
db_handler = None

# Import modules with graceful fallback
try:
    from models.yolo_detector import YOLODetector
except ImportError as e:
    print(f"Warning: YOLODetector not available: {e}")
    YOLODetector = None

try:
    from models.chemical_simulator import ChemicalSimulator, ChemicalReading
except ImportError as e:
    print(f"Warning: ChemicalSimulator not available: {e}")
    ChemicalSimulator = None
    ChemicalReading = None

try:
    from models.fusion_engine import FusionEngine
except ImportError as e:
    print(f"Warning: FusionEngine not available: {e}")
    FusionEngine = None

try:
    from utils.statistical_validator import StatisticalValidator
except ImportError as e:
    print(f"Warning: StatisticalValidator not available: {e}")
    StatisticalValidator = None

try:
    from database.db_handler import DatabaseHandler
except ImportError as e:
    print(f"Warning: DatabaseHandler not available: {e}")
    DatabaseHandler = None


def init_components():
    """Initialize all system components"""
    global yolo_detector, chemical_simulator, fusion_engine, statistical_validator, db_handler
    
    print("\n" + "=" * 70)
    print("Initializing Fruit Freshness Detection System")
    print("Technology Readiness Level 3 (Simulation-Based)")
    print("=" * 70 + "\n")
    
    # 1. Initialize YOLO Detector (Visual Component)
    try:
        if YOLODetector and config.MODEL_PATH.exists():
            print(f"Loading YOLO model from: {config.MODEL_PATH}")
            yolo_detector = YOLODetector(str(config.MODEL_PATH), str(config.DATA_YAML_PATH))
            print("✓ YOLO detector initialized (Visual Modality)")
        else:
            print("✗ YOLO detector unavailable - model file not found")
            print(f"  Set YOLO_MODEL_PATH to your weights .pt file, or place best.pt at:")
            print(f"    {config.BASE_DIR / 'models' / 'weights' / 'best.pt'}")
            print(f"    {config.BASE_DIR / 'data' / 'models' / 'yolov5n' / 'runs' / 'train' / 'yolov5n_fruit_ripeness' / 'weights' / 'best.pt'}")
    except Exception as e:
        print(f"✗ Error initializing YOLO: {e}")
        yolo_detector = None
    
    # 2. Initialize Chemical Simulator (FELIX-Inspired, TRL 3)
    try:
        if ChemicalSimulator:
            chemical_simulator = ChemicalSimulator(
                noise_sigma=config.SIMULATION_PARAMS['ethylene_noise_sigma'],
                temp_coeff=config.SIMULATION_PARAMS['temperature_coefficient'],
                humidity_coeff=config.SIMULATION_PARAMS['humidity_coefficient']
            )
            print("✓ Chemical simulator initialized (TRL 3 Simulation)")
            print(f"  Ethylene model: E(t) = E₀e^(kt)")
            print(f"  Noise model: Gaussian σ={config.SIMULATION_PARAMS['ethylene_noise_sigma']}")
    except Exception as e:
        print(f"✗ Error initializing chemical simulator: {e}")
        chemical_simulator = None
    
    # 3. Initialize Fusion Engine (Late Fusion 0.7/0.3)
    try:
        if FusionEngine:
            fusion_engine = FusionEngine(
                alpha=config.FUSION_WEIGHTS['alpha_visual'],
                beta=config.FUSION_WEIGHTS['beta_chemical'],
                delta=config.SIMULATION_PARAMS['conflict_threshold']
            )
            print(f"✓ Fusion engine initialized (Late Fusion {config.FUSION_WEIGHTS['alpha_visual']}/{config.FUSION_WEIGHTS['beta_chemical']})")
            print(f"  Conflict threshold δ={config.SIMULATION_PARAMS['conflict_threshold']}")
    except Exception as e:
        print(f"✗ Error initializing fusion engine: {e}")
        fusion_engine = None
    
    # 4. Initialize Statistical Validator
    try:
        if StatisticalValidator:
            statistical_validator = StatisticalValidator(n_bootstrap=1000)
            print("✓ Statistical validator initialized (Bootstrap CI, McNemar's test)")
    except Exception as e:
        print(f"✗ Error initializing statistical validator: {e}")
        statistical_validator = None
    
    # 5. Initialize Database
    try:
        if DatabaseHandler:
            db_handler = DatabaseHandler()
            print("✓ Database handler initialized")
    except Exception as e:
        print(f"✗ Database handler unavailable: {e}")
        db_handler = None
    
    print("\n" + "=" * 70)
    print("System Ready")
    print("=" * 70 + "\n")


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


def extract_fruit_name(fruit_type: str) -> str:
    """Extract fruit name without ripeness descriptor"""
    if not fruit_type:
        return 'Unknown'
    
    ripeness_keywords = ['overripe', 'over-ripe', 'half-ripe', 'half ripe', 
                        'underripe', 'unripe', 'ripe', 'rotten', 'fresh']
    
    fruit_lower = fruit_type.lower()
    result = fruit_type
    
    for keyword in ripeness_keywords:
        pattern = r'\s+' + re.escape(keyword) + r'\s*$'
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        pattern = r'^\s*' + re.escape(keyword) + r'\s+'
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        pattern = r'\s+' + re.escape(keyword) + r'\s+'
        result = re.sub(pattern, ' ', result, flags=re.IGNORECASE)
    
    return re.sub(r'\s+', ' ', result).strip() or fruit_type


# ==================== ROUTES ====================

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
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
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
                    raw_fruit_type = fruit.get('type', 'Unknown')
                    fruit_type = extract_fruit_name(raw_fruit_type)
                    ripeness = fruit.get('ripeness', 'Unknown')
                    yolo_conf = fruit.get('yolo_confidence', 0) or 0
                    nir_conf = fruit.get('nir_confidence', 0) or 0
                    freshness_score = (yolo_conf * 0.7 + nir_conf * 0.3) * 100

                    entry = {
                        'scan_id': scan_details.get('scan_id'),
                        'timestamp': formatted_timestamp,
                        'raw_timestamp': timestamp,
                        'fruit_type': fruit_type,
                        'ripeness': ripeness,
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

    # Sample data if empty
    if not history_entries:
        sample_entries = [
            {
                'scan_id': 'demo-1',
                'timestamp': 'Nov 20, 2025 • 04:45 PM',
                'raw_timestamp': '2025-11-20T16:45:00',
                'fruit_type': 'Mango',
                'ripeness': 'Ripe',
                'freshness_score': 92.5,
                'yolo_confidence': 95.0,
                'nir_confidence': 88.0,
                'confidence': 93.0,
                'total_fruits': 4,
                'status': 'Completed',
                'processed_image_path': None
            }
        ]
        history_entries = sample_entries
        summary_stats['total_scans'] = 1
        summary_stats['total_fruits'] = 4
        summary_stats['latest_scan'] = sample_entries[0]['timestamp']
        fruit_types = {'Mango'}

    return render_template(
        'history.html',
        history_entries=history_entries,
        summary_stats=summary_stats,
        fruit_types=sorted(list(fruit_types))
    )


@app.route('/settings')
def settings():
    """Settings page"""
    detection_settings = {
        'confidence_threshold': config.CONFIDENCE_THRESHOLD,
        'iou_threshold': config.IOU_THRESHOLD,
        'model_path': str(config.MODEL_PATH),
        'max_upload_size_mb': round(config.MAX_UPLOAD_SIZE / (1024 * 1024), 1),
        'allowed_extensions': ', '.join(sorted(config.ALLOWED_EXTENSIONS))
    }

    simulation_settings = {
        'trl_level': '3 (Experimental Proof of Concept)',
        'ethylene_model': 'E(t) = E₀e^(kt)',
        'noise_sigma': config.SIMULATION_PARAMS['ethylene_noise_sigma'],
        'temp_coefficient': config.SIMULATION_PARAMS['temperature_coefficient'],
        'humidity_coefficient': config.SIMULATION_PARAMS['humidity_coefficient'],
        'disclaimer': 'Chemical sensing is mathematically simulated. Hardware validation required at TRL 4-5.'
    }

    fusion_settings = {
        'strategy': 'Late Fusion (Decision-Level)',
        'visual_weight': config.FUSION_WEIGHTS['alpha_visual'],
        'chemical_weight': config.FUSION_WEIGHTS['beta_chemical'],
        'conflict_threshold': config.SIMULATION_PARAMS['conflict_threshold'],
        'classification_thresholds': {
            'fresh': f">= {config.FRESHNESS_THRESHOLDS['fresh']}",
            'ripe': f"{config.FRESHNESS_THRESHOLDS['ripe']} - {config.FRESHNESS_THRESHOLDS['fresh']}",
            'overripe': f"< {config.FRESHNESS_THRESHOLDS['ripe']}"
        }
    }

    system_status = {
        'yolo_detector': 'Connected' if yolo_detector else 'Not Available',
        'chemical_simulator': 'Active (TRL 3)' if chemical_simulator else 'Not Available',
        'fusion_engine': 'Ready' if fusion_engine else 'Not Available',
        'statistical_validator': 'Ready' if statistical_validator else 'Not Available',
        'database': 'Connected' if db_handler else 'Unavailable'
    }

    return render_template(
        'settings.html',
        detection_settings=detection_settings,
        simulation_settings=simulation_settings,
        fusion_settings=fusion_settings,
        system_status=system_status
    )


@app.route('/api/detect', methods=['POST'])
def detect():
    """
    Main detection endpoint implementing bimodal fusion (TRL 3)
    
    Process:
    1. YOLO object detection (visual)
    2. Chemical simulation (FELIX-inspired)
    3. Late fusion (0.7/0.3 with conflict resolution)
    4. Statistical validation
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    
    try:
        # Get simulation parameters from request
        hours = float(request.form.get('hours_since_harvest', 24))
        temp = float(request.form.get('temperature', config.SIMULATION_PARAMS['nominal_temperature']))
        humidity = float(request.form.get('humidity', config.SIMULATION_PARAMS['nominal_humidity']))
        
        # Save uploaded file
        scan_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{scan_id}.{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)
        
        # Check YOLO availability
        if not yolo_detector:
            return jsonify({
                'success': False, 
                'error': 'YOLO detector not initialized. Check model file.'
            }), 500
        
        # Step 1: YOLO Detection (Visual Modality)
        yolo_results = yolo_detector.detect(filepath)
        
        # Step 2: Chemical Simulation (FELIX-Inspired, TRL 3)
        chemical_readings = []
        if chemical_simulator:
            for det in yolo_results:
                fruit_type = extract_fruit_name(det.get('class_name', 'unknown'))
                # Add small variation to hours per fruit (simulating batch heterogeneity)
                hours_var = hours + np.random.uniform(-2, 2)
                chem_result = chemical_simulator.simulate(
                    fruit_type=fruit_type,
                    hours_since_harvest=max(0, hours_var),
                    temperature=temp,
                    humidity=humidity
                )
                chemical_readings.append(chem_result)
        else:
            # Fallback if simulator unavailable
            for det in yolo_results:
                chemical_readings.append({
                    'normalized_proxy': 0.5,
                    'ethylene_ppm': 0.5,
                    'brix_estimate': 12.0,
                    'moisture_estimate': 80.0
                })
        
        # Step 3: Late Fusion (Decision-Level Integration)
        fused_results = []
        if fusion_engine and chemical_simulator:
            # Prepare YOLO results format
            yolo_prepared = [{
                'bbox': det.get('bbox', det.get('box', [])),
                'fruit_type': extract_fruit_name(det.get('class_name', 'unknown')),
                'class_name': det.get('class_name', 'unknown'),
                'confidence': det.get('confidence', 0)
            } for det in yolo_results]
            
            fused_results = fusion_engine.batch_fuse(yolo_prepared, chemical_readings)
        else:
            # Fallback to YOLO-only
            for i, det in enumerate(yolo_results):
                conf = det.get('confidence', 0)
                classification = 'Ripe' if conf > 0.7 else 'Unripe' if conf < 0.4 else 'Overripe'
                fused_results.append({
                    **det,
                    'fusion_score': conf,
                    'classification': classification,
                    'fusion_method': 'yolo_only_fallback',
                    'has_conflict': False
                })
        
        # Save annotated image
        processed_filename = f"{scan_id}_processed.jpg"
        processed_path = os.path.join(str(config.PROCESSED_FOLDER), processed_filename)
        yolo_detector.save_annotated_image(filepath, processed_path, fused_results)
        
        # Prepare response data with TRL 3 transparency
        fruits_data = []
        for i, (fused, chem) in enumerate(zip(fused_results, chemical_readings)):
            chem_dict = chem if isinstance(chem, dict) else {
                'ethylene_ppm': chem.ethylene_ppm,
                'normalized_proxy': chem.normalized_proxy,
                'brix_estimate': chem.brix_estimate,
                'moisture_estimate': chem.moisture_estimate,
                'composite_quality': chem.composite_quality
            }
            
            fruits_data.append({
                'type': fused.get('fruit_type', 'Unknown'),
                'ripeness': fused.get('classification', 'Unknown'),
                'confidence': round(fused.get('fusion_score', 0), 3),
                'yolo_confidence': round(fused.get('yolo_confidence', fused.get('confidence', 0)), 3),
                'nir_confidence': round(chem_dict['normalized_proxy'], 3),
                'chemical_data': {
                    'ethylene_ppm': round(chem_dict['ethylene_ppm'], 3),
                    'brix': chem_dict['brix_estimate'],
                    'moisture': chem_dict['moisture_estimate'],
                    'composite_quality': chem_dict.get('composite_quality', 0)
                },
                'fusion_details': {
                    'has_conflict': fused.get('has_conflict', False),
                    'disagreement': round(fused.get('disagreement', 0), 3),
                    'resolution_strategy': fused.get('resolution_strategy', 'none'),
                    'weights': fused.get('weights_applied', {'alpha': 0.7, 'beta': 0.3})
                },
                'bbox': fused.get('bbox', [])
            })
        
        # Calculate statistics
        stats = {}
        if fusion_engine:
            stats = fusion_engine.get_statistics(fused_results)
        
        result_data = {
            'scan_id': scan_id,
            'trl_disclaimer': 'Technology Readiness Level 3 (Experimental Proof of Concept). '
                            'Chemical sensing is mathematically simulated using E(t)=E₀e^(kt). '
                            'No physical sensors deployed. Hardware validation required at TRL 4-5 '
                            'before operational deployment.',
            'simulation_metadata': {
                'ethylene_model': 'E(t) = E₀e^(kt)',
                'noise_model': f"Gaussian σ={config.SIMULATION_PARAMS['ethylene_noise_sigma']}",
                'temperature_sensitivity': f"±{config.SIMULATION_PARAMS['temperature_coefficient']*100:.0f}%",
                'fusion_weights': {
                    'visual': config.FUSION_WEIGHTS['alpha_visual'],
                    'chemical': config.FUSION_WEIGHTS['beta_chemical']
                },
                'classification_thresholds': {
                    'fresh': f">= {config.FRESHNESS_THRESHOLDS['fresh']}",
                    'ripe': f"{config.FRESHNESS_THRESHOLDS['ripe']} - {config.FRESHNESS_THRESHOLDS['fresh']}",
                    'overripe': f"< {config.FRESHNESS_THRESHOLDS['ripe']}"
                },
                'input_conditions': {
                    'hours_since_harvest': hours,
                    'temperature_c': temp,
                    'humidity_percent': humidity
                }
            },
            'total_fruits': len(fused_results),
            'fruits': fruits_data,
            'statistics': stats
        }
        
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
        error_trace = traceback.format_exc()
        print(f"Error in detection: {e}")
        print(error_trace)
        
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': error_trace if config.DEBUG else None
        }), 500


@app.route('/api/sensitivity-test', methods=['POST'])
def sensitivity_test():
    """
    Sensitivity Analysis endpoint (Thesis Section 4.1.6)
    Tests robustness by varying simulation parameters ±20%
    """
    try:
        data = request.get_json() or {}
        fruit_type = data.get('fruit_type', 'mango').lower()
        base_hours = float(data.get('hours_since_harvest', 24))
        base_temp = float(data.get('temperature', 25))
        
        if not chemical_simulator:
            return jsonify({'error': 'Chemical simulator not available'}), 500
        
        if fruit_type not in chemical_simulator.ETHYLENE_PARAMS:
            return jsonify({'error': f'Unknown fruit type: {fruit_type}'}), 400
        
        # Baseline simulation
        baseline = chemical_simulator.simulate(fruit_type, base_hours, base_temp)
        # Tier thresholds match fusion _classify_freshness (applied here to proxy-only stability)
        baseline_class = fusion_engine._classify_freshness(baseline.normalized_proxy) if fusion_engine else 'Unknown'
        
        # Test variations (±20%)
        variations = []
        test_cases = [
            ('E0_minus_20', 0.8, 1.0, 1.0, 1.0),   # E0 * 0.8
            ('E0_plus_20', 1.2, 1.0, 1.0, 1.0),    # E0 * 1.2
            ('k_minus_20', 1.0, 0.8, 1.0, 1.0),    # k * 0.8
            ('k_plus_20', 1.0, 1.2, 1.0, 1.0),     # k * 1.2
            ('temp_minus_20', 1.0, 1.0, 0.8, 1.0), # Temp factor 0.8
            ('temp_plus_20', 1.0, 1.0, 1.2, 1.0),  # Temp factor 1.2
            ('noise_extreme', 1.0, 1.0, 1.0, 2.0), # Double noise
        ]
        
        params = chemical_simulator.ETHYLENE_PARAMS[fruit_type]
        base_E0, base_k = params['E0'], params['k']
        
        for label, e0_f, k_f, temp_f, noise_f in test_cases:
            mod_temp = base_temp + (10 * (temp_f - 1.0)) if temp_f != 1.0 else base_temp
            result = chemical_simulator.simulate(
                fruit_type,
                base_hours,
                mod_temp,
                humidity=config.SIMULATION_PARAMS['nominal_humidity'],
                e0_factor=e0_f,
                k_factor=k_f,
                noise_scale=noise_f,
            )
            sp = result.simulation_params
            test_class = fusion_engine._classify_freshness(result.normalized_proxy) if fusion_engine else 'Unknown'
            stable = (test_class == baseline_class)
            
            variations.append({
                'parameter_variation': label,
                'modified_E0': round(sp.get('E0_effective', base_E0 * e0_f), 3),
                'modified_k': round(sp.get('k_effective', base_k * k_f), 4),
                'modified_temp': round(mod_temp, 1),
                'ethylene_ppm': round(result.ethylene_ppm, 3),
                'normalized_proxy': round(result.normalized_proxy, 3),
                'classification': test_class,
                'classification_stable': stable,
                'deviation_from_baseline': round(abs(result.normalized_proxy - baseline.normalized_proxy), 3)
            })
        
        stable_count = sum(1 for v in variations if v['classification_stable'])
        stability_rate = stable_count / len(variations)
        
        return jsonify({
            'success': True,
            'baseline': {
                'fruit_type': fruit_type,
                'ethylene_ppm': round(baseline.ethylene_ppm, 3),
                'normalized_proxy': round(baseline.normalized_proxy, 3),
                'classification': baseline_class,
                'parameters': {
                    'E0': base_E0,
                    'k': base_k,
                    'hours': base_hours,
                    'temperature': base_temp
                }
            },
            'variations': variations,
            'stability_rate': round(stability_rate, 2),
            'stable_classifications': stable_count,
            'total_variations': len(variations),
            'meets_criteria': stability_rate >= 0.67,  # At least 2/3 stable per thesis
            'note': 'Thesis Section 4.1.6: System should maintain >84.5% accuracy despite ±20% parameter variation'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/validate-batch', methods=['POST'])
def validate_batch():
    """
    Statistical validation endpoint
    Calculates Bootstrap CI and McNemar's test for significance
    """
    try:
        data = request.get_json() or {}
        yolo_correct = data.get('yolo_correct', [])  # List of booleans
        fusion_correct = data.get('fusion_correct', [])  # List of booleans
        yolo_scores = data.get('yolo_scores', [])  # List of floats (0-1)
        fusion_scores = data.get('fusion_scores', [])  # List of floats (0-1)
        
        if not statistical_validator:
            return jsonify({'error': 'Statistical validator not available'}), 500
        
        response = {'success': True}
        
        # Bootstrap Confidence Intervals
        if yolo_scores:
            y_mean, y_low, y_high = statistical_validator.bootstrap_confidence_interval(yolo_scores)
            response['yolo_confidence_ci'] = {
                'mean': round(y_mean, 3),
                '95_percent_ci': [round(y_low, 3), round(y_high, 3)],
                'n_samples': len(yolo_scores)
            }
        
        if fusion_scores:
            f_mean, f_low, f_high = statistical_validator.bootstrap_confidence_interval(fusion_scores)
            response['fusion_confidence_ci'] = {
                'mean': round(f_mean, 3),
                '95_percent_ci': [round(f_low, 3), round(f_high, 3)],
                'n_samples': len(fusion_scores)
            }
        
        # McNemar's Test (paired comparison)
        if yolo_correct and fusion_correct and len(yolo_correct) == len(fusion_correct):
            mcnemar = statistical_validator.mcnemar_test(yolo_correct, fusion_correct)
            response['mcnemar_test'] = mcnemar
            response['significance_note'] = 'Significant if p < 0.05 (fusion improvement not due to chance)'
        
        chemical_proxies = data.get('chemical_proxies')
        if yolo_scores and chemical_proxies and len(yolo_scores) == len(chemical_proxies):
            consistency = statistical_validator.cross_modal_consistency(yolo_scores, chemical_proxies)
            response['cross_modal_consistency'] = consistency
        elif yolo_scores and fusion_scores and len(yolo_scores) == len(fusion_scores):
            consistency = statistical_validator.cross_modal_consistency(yolo_scores, fusion_scores)
            response['cross_modal_consistency'] = consistency
            response['cross_modal_consistency_note'] = (
                'Second series was labeled fusion_scores; use chemical_proxies for YOLO vs chemical proxy correlation.'
            )
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/results/<scan_id>')
def results(scan_id):
    """Display results page"""
    try:
        if db_handler:
            scan_data = db_handler.get_scan(scan_id)
            if scan_data:
                results_data = scan_data.get('results', {})
                fruits = results_data.get('fruits', [])
                
                total_fruits = len(fruits)
                def _rlabel(f):
                    return (f.get('ripeness') or '').strip().lower()
                fresh_count = sum(1 for f in fruits if _rlabel(f) == 'fresh')
                ripe_count = sum(1 for f in fruits if _rlabel(f) == 'ripe')
                overripe_count = sum(1 for f in fruits if _rlabel(f) == 'overripe')
                legacy_unripe = sum(1 for f in fruits if _rlabel(f) in ('unripe', 'underripe'))
                if legacy_unripe and fresh_count == 0:
                    fresh_count = legacy_unripe
                
                result_image = f"/static/images/processed/{scan_id}_processed.jpg"
                
                return render_template('results.html',
                    result_image=result_image,
                    fruits=fruits,
                    total_fruits=total_fruits,
                    fresh_count=fresh_count,
                    ripe_count=ripe_count,
                    overripe_count=overripe_count,
                    trl_disclaimer='TRL 3 Simulation - Chemical data mathematically modeled'
                )
        
        return render_template('results.html',
            result_image="/static/images/placeholder.jpg",
            fruits=[],
            total_fruits=0,
            fresh_count=0,
            ripe_count=0,
            overripe_count=0
        )
    
    except Exception as e:
        print(f"Error loading results: {e}")
        return redirect(url_for('index'))


@app.route('/api/export/<scan_id>')
def export_results(scan_id):
    """Export scan results as formatted text file"""
    try:
        if db_handler:
            scan_data = db_handler.get_scan(scan_id)
            if scan_data:
                timestamp = scan_data.get('timestamp', 'Unknown')
                fruits = scan_data.get('fruits', [])
                
                try:
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%B %d, %Y at %I:%M %p')
                    else:
                        formatted_time = 'Unknown'
                except:
                    formatted_time = timestamp if timestamp else 'Unknown'
                
                output = io.StringIO()
                output.write("=" * 70 + "\n")
                output.write("FRUIT FRESHNESS DETECTION REPORT\n")
                output.write("Technology Readiness Level 3 (Simulation-Based)\n")
                output.write("=" * 70 + "\n\n")
                output.write(f"Scan ID:        {scan_id}\n")
                output.write(f"Scan Date:      {formatted_time}\n")
                output.write(f"Total Fruits:   {len(fruits)}\n")
                output.write("\nDISCLAIMER: Chemical sensing data is mathematically simulated.\n")
                output.write("Ethylene model: E(t) = E₀e^(kt) with Gaussian noise.\n")
                output.write("Hardware validation required at TRL 4-5.\n\n")
                
                if fruits:
                    output.write("DETECTED FRUITS\n")
                    output.write("-" * 70 + "\n")
                    for idx, fruit in enumerate(fruits, 1):
                        output.write(f"\nFruit #{idx}: {fruit.get('type', 'Unknown')}\n")
                        output.write(f"  Ripeness:        {fruit.get('ripeness', 'Unknown')}\n")
                        output.write(f"  Fusion Score:    {fruit.get('confidence', 0):.1%}\n")
                        output.write(f"  YOLO Conf:       {fruit.get('yolo_confidence', 0):.1%}\n")
                        output.write(f"  Chemical Proxy:  {fruit.get('nir_confidence', 0):.1%}\n")
                        chem = fruit.get('chemical_data', {})
                        if chem:
                            output.write(f"  Ethylene:        {chem.get('ethylene_ppm', 'N/A')} ppm\n")
                            output.write(f"  Est. Brix:       {chem.get('brix', 'N/A')}°\n")
                
                output.write("\n" + "=" * 70 + "\n")
                output.seek(0)
                
                return send_file(
                    io.BytesIO(output.getvalue().encode('utf-8')),
                    mimetype='text/plain',
                    as_attachment=True,
                    download_name=f'fruit_scan_{scan_id}_TRL3.txt'
                )
        
        return jsonify({'error': 'Results not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-history')
def export_history():
    """Export all history as CSV"""
    try:
        if not db_handler:
            return jsonify({'error': 'Database not available'}), 500
        
        scans = db_handler.get_all_scans(limit=10000)
        if not scans:
            return jsonify({'error': 'No history found'}), 404
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Scan ID', 'Timestamp', 'Fruit Type', 'Ripeness', 
                        'Fusion Score', 'YOLO Conf', 'Chemical Proxy', 
                        'Ethylene ppm', 'Brix', 'Moisture'])
        
        for scan in scans:
            scan_details = db_handler.get_scan(scan.get('scan_id'))
            if scan_details:
                for fruit in scan_details.get('fruits', []):
                    chem = fruit.get('chemical_data', {})
                    writer.writerow([
                        scan.get('scan_id'),
                        scan_details.get('timestamp'),
                        fruit.get('type', ''),
                        fruit.get('ripeness', ''),
                        fruit.get('confidence', ''),
                        fruit.get('yolo_confidence', ''),
                        fruit.get('nir_confidence', ''),
                        chem.get('ethylene_ppm', ''),
                        chem.get('brix', ''),
                        chem.get('moisture', '')
                    ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'fruit_scanner_history_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear all scan history"""
    try:
        if not db_handler:
            return jsonify({'success': False, 'error': 'Database not available'}), 500
        
        success = db_handler.clear_all_scans()
        return jsonify({
            'success': success,
            'message': 'History cleared' if success else 'Failed to clear'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'error': 'File too large (max 16MB)'}), 413

@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    init_components()
    print(f"\nStarting server on http://{config.HOST}:{config.PORT}")
    print(f"Debug mode: {config.DEBUG}\n")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)