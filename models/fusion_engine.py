"""
Fusion Engine for combining YOLO detection and NIR analysis
"""
from typing import List, Dict, Optional
import numpy as np
from models.yolo_detector import YOLODetector
from nir.nir_scanner import NIRScannerBase


class FusionEngine:
    """Engine to fuse YOLO detection and NIR analysis results"""
    
    def __init__(self, yolo_detector: YOLODetector, nir_scanner: NIRScannerBase):
        """
        Initialize fusion engine
        
        Args:
            yolo_detector: YOLO detector instance
            nir_scanner: NIR scanner instance
        """
        self.yolo_detector = yolo_detector
        self.nir_scanner = nir_scanner
        
        # Fusion weights (YOLO: 0.6, Felix/NIR: 0.4 as per conceptual framework)
        self.yolo_weight = 0.6  # Weight for YOLO detection
        self.nir_weight = 0.4   # Weight for Felix/NIR analysis
        
        print("Fusion Engine initialized")
    
    def fuse_detections(self, yolo_results: List[Dict], image_path: str) -> List[Dict]:
        """
        Fuse YOLO detection results with NIR analysis
        
        Args:
            yolo_results: List of YOLO detection results
            image_path: Path to the image for NIR scanning
        
        Returns:
            List of fused detection results with enhanced quality assessment
        """
        fused_results = []
        
        for detection in yolo_results:
            # Get bounding box
            bbox = detection['bbox']
            x1, y1, x2, y2 = bbox
            
            # Perform NIR scan on detected region
            try:
                nir_result = self.nir_scanner.scan(region=(int(x1), int(y1), int(x2), int(y2)))
                nir_analysis = nir_result.get('analysis', {})
            except Exception as e:
                print(f"Warning: NIR scan failed for region {bbox}: {e}")
                # Use default NIR analysis if scan fails
                nir_analysis = {
                    'ripeness_score': 0.5,
                    'ripeness_category': 'Unknown',
                    'quality_score': 0.5,
                    'confidence': 0.5
                }
            
            # Fuse YOLO and NIR results
            fused_detection = self._fuse_single_detection(detection, nir_analysis)
            fused_results.append(fused_detection)
        
        return fused_results
    
    def _fuse_single_detection(self, yolo_detection: Dict, nir_analysis: Dict) -> Dict:
        """
        Fuse a single YOLO detection with NIR analysis
        
        Args:
            yolo_detection: Single YOLO detection result
            nir_analysis: NIR analysis result
        
        Returns:
            Fused detection result
        """
        # Extract YOLO information
        yolo_class = yolo_detection.get('class_name', 'Unknown')
        yolo_confidence = yolo_detection.get('confidence', 0.5)
        yolo_quality = yolo_detection.get('quality_status', 'unknown')
        yolo_ripeness = yolo_detection.get('ripeness', 'Unknown')
        
        # Extract NIR information
        nir_ripeness = nir_analysis.get('ripeness_category', 'Unknown')
        nir_quality_score = nir_analysis.get('quality_score', 0.5)
        nir_confidence = nir_analysis.get('confidence', 0.5)
        
        # Fuse ripeness assessment
        # If YOLO and NIR agree, increase confidence
        # If they disagree, use weighted average
        yolo_ripeness_lower = yolo_ripeness.lower()
        nir_ripeness_lower = nir_ripeness.lower()
        
        # Check if ripeness assessments are similar
        ripeness_agreement = self._check_ripeness_agreement(yolo_ripeness_lower, nir_ripeness_lower)
        
        # Determine final ripeness
        if ripeness_agreement:
            # High agreement - use YOLO result with boosted confidence
            final_ripeness = yolo_ripeness
            ripeness_confidence = min(1.0, (yolo_confidence + nir_confidence) / 2 + 0.1)
        else:
            # Disagreement - use weighted combination
            # Prefer YOLO for type, NIR for ripeness assessment
            final_ripeness = self._combine_ripeness(yolo_ripeness, nir_ripeness, yolo_confidence, nir_confidence)
            ripeness_confidence = (yolo_confidence + nir_confidence) / 2
        
        # Fuse quality status
        final_quality = self._fuse_quality_status(yolo_quality, nir_quality_score, yolo_confidence, nir_confidence)
        
        # Calculate overall confidence (weighted average)
        overall_confidence = (yolo_confidence * self.yolo_weight + nir_confidence * self.nir_weight)
        
        # Build fused result
        fused_result = {
            'bbox': yolo_detection['bbox'],
            'class_id': yolo_detection['class_id'],
            'class_name': yolo_class,
            'confidence': overall_confidence,
            'yolo_confidence': yolo_confidence,
            'nir_confidence': nir_confidence,
            'quality_status': final_quality,
            'ripeness': final_ripeness,
            'yolo_ripeness': yolo_ripeness,
            'nir_ripeness': nir_ripeness,
            'ripeness_confidence': ripeness_confidence,
            'nir_quality_score': nir_quality_score,
            'fusion_method': 'weighted_average',
            'agreement': 'high' if ripeness_agreement else 'moderate'
        }
        
        return fused_result
    
    def _check_ripeness_agreement(self, yolo_ripeness: str, nir_ripeness: str) -> bool:
        """
        Check if YOLO and NIR ripeness assessments agree
        
        Args:
            yolo_ripeness: YOLO ripeness assessment (lowercase)
            nir_ripeness: NIR ripeness assessment (lowercase)
        
        Returns:
            True if assessments agree, False otherwise
        """
        # Define ripeness categories
        unripe_keywords = ['unripe', 'underripe']
        half_ripe_keywords = ['half-ripe', 'half ripe']
        ripe_keywords = ['ripe']
        overripe_keywords = ['overripe', 'over-ripe']
        
        # Categorize YOLO ripeness
        yolo_category = None
        if any(kw in yolo_ripeness for kw in unripe_keywords):
            yolo_category = 'unripe'
        elif any(kw in yolo_ripeness for kw in half_ripe_keywords):
            yolo_category = 'half-ripe'
        elif any(kw in yolo_ripeness for kw in ripe_keywords) and not any(kw in yolo_ripeness for kw in overripe_keywords):
            yolo_category = 'ripe'
        elif any(kw in yolo_ripeness for kw in overripe_keywords):
            yolo_category = 'overripe'
        
        # Categorize NIR ripeness
        nir_category = None
        if any(kw in nir_ripeness for kw in unripe_keywords):
            nir_category = 'unripe'
        elif any(kw in nir_ripeness for kw in half_ripe_keywords):
            nir_category = 'half-ripe'
        elif any(kw in nir_ripeness for kw in ripe_keywords) and not any(kw in nir_ripeness for kw in overripe_keywords):
            nir_category = 'ripe'
        elif any(kw in nir_ripeness for kw in overripe_keywords):
            nir_category = 'overripe'
        
        # Check agreement (allow adjacent categories as agreement)
        if yolo_category == nir_category:
            return True
        elif yolo_category and nir_category:
            # Check if categories are adjacent (e.g., unripe and half-ripe)
            category_order = ['unripe', 'half-ripe', 'ripe', 'overripe']
            try:
                yolo_idx = category_order.index(yolo_category)
                nir_idx = category_order.index(nir_category)
                return abs(yolo_idx - nir_idx) <= 1
            except ValueError:
                return False
        
        return False
    
    def _combine_ripeness(self, yolo_ripeness: str, nir_ripeness: str, 
                         yolo_conf: float, nir_conf: float) -> str:
        """
        Combine YOLO and NIR ripeness assessments
        
        Args:
            yolo_ripeness: YOLO ripeness assessment
            nir_ripeness: NIR ripeness assessment
            yolo_conf: YOLO confidence
            nir_conf: NIR confidence
        
        Returns:
            Combined ripeness assessment
        """
        # Weighted decision: prefer higher confidence source
        if yolo_conf > nir_conf + 0.2:
            return yolo_ripeness
        elif nir_conf > yolo_conf + 0.2:
            return nir_ripeness
        else:
            # Similar confidence - prefer NIR for ripeness (more accurate for quality)
            return nir_ripeness
    
    def _fuse_quality_status(self, yolo_quality: str, nir_quality_score: float,
                            yolo_conf: float, nir_conf: float) -> str:
        """
        Fuse quality status from YOLO and NIR
        
        Args:
            yolo_quality: YOLO quality status
            nir_quality_score: NIR quality score (0-1)
            yolo_conf: YOLO confidence
            nir_conf: NIR confidence
        
        Returns:
            Fused quality status
        """
        # Map NIR quality score to status
        if nir_quality_score >= 0.8:
            nir_quality = 'fresh'
        elif nir_quality_score >= 0.6:
            nir_quality = 'ripe'
        elif nir_quality_score >= 0.4:
            nir_quality = 'unripe'
        else:
            nir_quality = 'overripe'
        
        # Combine with YOLO quality
        # If both agree, use that
        if yolo_quality == nir_quality:
            return yolo_quality
        
        # If disagree, use weighted decision
        combined_score = (nir_quality_score * self.nir_weight + 
                         (0.8 if yolo_quality == 'fresh' else 0.6 if yolo_quality == 'ripe' else 0.4) * self.yolo_weight)
        
        if combined_score >= 0.75:
            return 'fresh'
        elif combined_score >= 0.55:
            return 'ripe'
        elif combined_score >= 0.35:
            return 'unripe'
        else:
            return 'overripe'
    
    def set_fusion_weights(self, yolo_weight: float, nir_weight: float):
        """
        Set fusion weights for YOLO and NIR
        
        Args:
            yolo_weight: Weight for YOLO detection (0-1)
            nir_weight: Weight for NIR analysis (0-1)
        """
        if abs(yolo_weight + nir_weight - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")
        
        self.yolo_weight = yolo_weight
        self.nir_weight = nir_weight
        print(f"Fusion weights updated: YOLO={yolo_weight}, NIR={nir_weight}")

