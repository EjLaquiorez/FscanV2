"""
Database handler for Fruit Quality Scanner
Supports SQLite, PostgreSQL, and MySQL
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Dict, List, Optional
import json

from config import DATABASE_URL, DATABASE_TYPE

Base = declarative_base()


class Scan(Base):
    """Scan table - stores scan metadata"""
    __tablename__ = 'scans'
    
    id = Column(String, primary_key=True)  # scan_id (UUID)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    image_path = Column(String, nullable=False)
    processed_image_path = Column(String)
    results_json = Column(JSON)  # Store full results as JSON
    total_fruits = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to fruits
    fruits = relationship("Fruit", back_populates="scan", cascade="all, delete-orphan")


class Fruit(Base):
    """Fruit table - stores individual fruit detection results"""
    __tablename__ = 'fruits'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String, ForeignKey('scans.id'), nullable=False)
    fruit_type = Column(String, nullable=False)
    class_id = Column(Integer)
    class_name = Column(String)
    quality_status = Column(String)
    ripeness = Column(String)
    confidence = Column(Float)
    yolo_confidence = Column(Float)
    nir_confidence = Column(Float)
    bbox_x1 = Column(Float)
    bbox_y1 = Column(Float)
    bbox_x2 = Column(Float)
    bbox_y2 = Column(Float)
    nir_quality_score = Column(Float)
    fusion_method = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to scan
    scan = relationship("Scan", back_populates="fruits")


class DatabaseHandler:
    """Handler for database operations"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database handler
        
        Args:
            database_url: Optional database URL (uses config default if not provided)
        """
        self.database_url = database_url or DATABASE_URL
        self.database_type = DATABASE_TYPE
        
        # Create engine
        # For SQLite, use check_same_thread=False for Flask
        if self.database_type == 'sqlite':
            self.engine = create_engine(
                self.database_url,
                connect_args={'check_same_thread': False},
                echo=False
            )
        else:
            self.engine = create_engine(self.database_url, echo=False)
        
        # Create session factory
        SessionLocal = sessionmaker(bind=self.engine)
        self.SessionLocal = SessionLocal
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        print(f"Database handler initialized ({self.database_type})")
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def save_scan(self, scan_id: str, image_path: str, processed_image_path: str, 
                  results_data: Dict) -> bool:
        """
        Save scan results to database
        
        Args:
            scan_id: Unique scan ID (UUID)
            image_path: Path to original image
            processed_image_path: Path to processed/annotated image
            results_data: Dictionary with scan results
        
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.get_session()
            
            # Extract data
            results = results_data.get('results', [])
            total_fruits = results_data.get('total_fruits', len(results))
            
            # Create scan record
            scan = Scan(
                id=scan_id,
                timestamp=datetime.utcnow(),
                image_path=image_path,
                processed_image_path=processed_image_path,
                results_json=results_data,
                total_fruits=total_fruits
            )
            
            session.add(scan)
            
            # Create fruit records
            fruits_data = results_data.get('fruits', [])
            for fruit_data in fruits_data:
                # Get corresponding result for bbox
                result = next((r for r in results if r.get('class_name') == fruit_data.get('type')), {})
                bbox = result.get('bbox', [0, 0, 0, 0])
                
                fruit = Fruit(
                    scan_id=scan_id,
                    fruit_type=fruit_data.get('type', 'Unknown'),
                    class_id=result.get('class_id'),
                    class_name=fruit_data.get('type', 'Unknown'),
                    quality_status=fruit_data.get('quality_status', 'unknown'),
                    ripeness=fruit_data.get('ripeness', 'Unknown'),
                    confidence=fruit_data.get('confidence', 0.0),
                    yolo_confidence=result.get('yolo_confidence', fruit_data.get('confidence', 0.0)),
                    nir_confidence=result.get('nir_confidence', 0.0),
                    bbox_x1=bbox[0] if len(bbox) > 0 else 0,
                    bbox_y1=bbox[1] if len(bbox) > 1 else 0,
                    bbox_x2=bbox[2] if len(bbox) > 2 else 0,
                    bbox_y2=bbox[3] if len(bbox) > 3 else 0,
                    nir_quality_score=result.get('nir_quality_score'),
                    fusion_method=result.get('fusion_method', 'yolo_only')
                )
                
                session.add(fruit)
            
            session.commit()
            session.close()
            
            print(f"Scan {scan_id} saved to database")
            return True
        
        except Exception as e:
            print(f"Error saving scan to database: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def get_scan(self, scan_id: str) -> Optional[Dict]:
        """
        Get scan data from database
        
        Args:
            scan_id: Scan ID to retrieve
        
        Returns:
            Dictionary with scan data, or None if not found
        """
        try:
            session = self.get_session()
            
            scan = session.query(Scan).filter(Scan.id == scan_id).first()
            
            if not scan:
                session.close()
                return None
            
            # Get fruits
            fruits = session.query(Fruit).filter(Fruit.scan_id == scan_id).all()
            
            # Build result dictionary
            result = {
                'scan_id': scan.id,
                'timestamp': scan.timestamp.isoformat() if scan.timestamp else None,
                'image_path': scan.image_path,
                'processed_image_path': scan.processed_image_path,
                'total_fruits': scan.total_fruits,
                'results': scan.results_json or {},
                'fruits': [
                    {
                        'type': f.fruit_type,
                        'class_id': f.class_id,
                        'quality_status': f.quality_status,
                        'ripeness': f.ripeness,
                        'confidence': f.confidence,
                        'yolo_confidence': f.yolo_confidence,
                        'nir_confidence': f.nir_confidence,
                        'bbox': [f.bbox_x1, f.bbox_y1, f.bbox_x2, f.bbox_y2],
                        'nir_quality_score': f.nir_quality_score
                    }
                    for f in fruits
                ]
            }
            
            session.close()
            return result
        
        except Exception as e:
            print(f"Error getting scan from database: {e}")
            if 'session' in locals():
                session.close()
            return None
    
    def get_all_scans(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get all scans with pagination
        
        Args:
            limit: Maximum number of scans to return
            offset: Number of scans to skip
        
        Returns:
            List of scan dictionaries
        """
        try:
            session = self.get_session()
            
            scans = session.query(Scan).order_by(Scan.timestamp.desc()).limit(limit).offset(offset).all()
            
            results = []
            for scan in scans:
                results.append({
                    'scan_id': scan.id,
                    'timestamp': scan.timestamp.isoformat() if scan.timestamp else None,
                    'total_fruits': scan.total_fruits,
                    'image_path': scan.image_path
                })
            
            session.close()
            return results
        
        except Exception as e:
            print(f"Error getting scans from database: {e}")
            if 'session' in locals():
                session.close()
            return []
    
    def delete_scan(self, scan_id: str) -> bool:
        """
        Delete scan from database
        
        Args:
            scan_id: Scan ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.get_session()
            
            scan = session.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                session.delete(scan)
                session.commit()
                session.close()
                print(f"Scan {scan_id} deleted from database")
                return True
            else:
                session.close()
                return False
        
        except Exception as e:
            print(f"Error deleting scan from database: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about scans
        
        Returns:
            Dictionary with statistics
        """
        try:
            session = self.get_session()
            
            total_scans = session.query(Scan).count()
            total_fruits = session.query(Fruit).count()
            
            # Count by fruit type
            fruit_types = session.query(Fruit.fruit_type, session.query(Fruit).filter(
                Fruit.fruit_type == Fruit.fruit_type
            ).count()).distinct().all()
            
            type_counts = {}
            for fruit_type, count in fruit_types:
                type_counts[fruit_type] = count
            
            # Count by quality status
            quality_counts = {}
            quality_statuses = session.query(Fruit.quality_status).distinct().all()
            for (status,) in quality_statuses:
                count = session.query(Fruit).filter(Fruit.quality_status == status).count()
                quality_counts[status] = count
            
            session.close()
            
            return {
                'total_scans': total_scans,
                'total_fruits': total_fruits,
                'fruit_type_counts': type_counts,
                'quality_status_counts': quality_counts
            }
        
        except Exception as e:
            print(f"Error getting statistics from database: {e}")
            if 'session' in locals():
                session.close()
            return {
                'total_scans': 0,
                'total_fruits': 0,
                'fruit_type_counts': {},
                'quality_status_counts': {}
            }

