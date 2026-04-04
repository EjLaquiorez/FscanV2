"""
Configuration settings for Fruit Quality Scanner application
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Allows importing this module before `pip install python-dotenv`
    pass

# Base directory
BASE_DIR = Path(__file__).parent

# Flask configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'  # Enable debug by default
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# Upload configuration
UPLOAD_FOLDER = BASE_DIR / 'static' / 'images' / 'uploads'
PROCESSED_FOLDER = BASE_DIR / 'static' / 'images' / 'processed'
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# YOLO model configuration
# Using the trained model from data/models/yolov5n/runs folder
MODEL_PATH = BASE_DIR / 'data' / 'models' / 'yolov5n' / 'runs' / 'train' / 'yolov5n_fruit_ripeness' / 'weights' / 'best.pt'
DATA_YAML_PATH = BASE_DIR / 'data' / 'datasets' / 'Fruit_dataset' / 'data.yaml'
CONFIDENCE_THRESHOLD = float(os.getenv('YOLO_CONFIDENCE', 0.25))
IOU_THRESHOLD = float(os.getenv('YOLO_IOU', 0.45))

# NIR scanner configuration
NIR_ENABLED = os.getenv('NIR_ENABLED', 'True').lower() == 'true'
NIR_MOCK_MODE = os.getenv('NIR_MOCK_MODE', 'True').lower() == 'true'
NIR_DEVICE_ID = os.getenv('NIR_DEVICE_ID', None)
NIR_API_URL = os.getenv('NIR_API_URL', None)

# Database configuration
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')  # sqlite, postgresql, mysql

# SQLite configuration (default)
SQLITE_DB_PATH = BASE_DIR / 'database' / 'fruit_scanner.db'

# PostgreSQL configuration
POSTGRESQL_HOST = os.getenv('POSTGRESQL_HOST', 'localhost')
POSTGRESQL_PORT = int(os.getenv('POSTGRESQL_PORT', 5432))
POSTGRESQL_DB = os.getenv('POSTGRESQL_DB', 'fruit_scanner')
POSTGRESQL_USER = os.getenv('POSTGRESQL_USER', 'postgres')
POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD', '')

# MySQL configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_DB = os.getenv('MYSQL_DB', 'fruit_scanner')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')

# Database URL construction
if DATABASE_TYPE == 'postgresql':
    # SQLAlchemy dialect for psycopg v3 (see requirements.txt psycopg[binary])
    DATABASE_URL = (
        f'postgresql+psycopg://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}'
        f'@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}'
    )
elif DATABASE_TYPE == 'mysql':
    DATABASE_URL = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
else:
    # SQLite (default)
    DATABASE_URL = f'sqlite:///{SQLITE_DB_PATH}'

# Create necessary directories
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
(BASE_DIR / 'database').mkdir(parents=True, exist_ok=True)

# TRL 3 Simulation Settings
SIMULATION_PARAMS = {
    'ethylene_noise_sigma': 0.05,      # Gaussian noise from Voss et al.
    'temperature_coefficient': 0.15,    # ±15% sensitivity
    'humidity_coefficient': 0.05,       # γ = 0.05
    'nominal_temperature': 25,          # 25°C baseline
    'nominal_humidity': 80,             # 80% RH baseline
    'conflict_threshold': 0.15          # δ = 0.15 for fusion conflict
}

# Fusion Weights (Thesis validated)
FUSION_WEIGHTS = {
    'visual_alpha': 0.7,      # YOLO weight
    'chemical_beta': 0.3,     # Chemical proxy weight
    'conflict_boost_yolo': 0.9,   # When YOLO >> Chemical
    'conflict_boost_chem': 0.4    # When Chemical >> YOLO (conservative)
}

# Classification Thresholds (Thesis Table 3.3.4)
FRESHNESS_THRESHOLDS = {
    'fresh': 0.80,      # F(t) >= 0.80
    'ripe': 0.65,       # 0.65 <= F(t) < 0.80
    'overripe': 0.00    # F(t) < 0.65
}