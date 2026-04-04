"""
Late Fusion Engine (Decision-Level Integration)
Thesis specification: α=0.7 (visual), β=0.3 (chemical), δ=0.15 conflict threshold
"""
import numpy as np
from typing import Dict, List
from dataclasses import asdict


class FusionEngine:
    """
    Implements Late Fusion strategy per thesis Section 3.3
    F(t) = α·C_YOLO + β·Ê(t)
    """
    
    def __init__(self, alpha: float = 0.7, beta: float = 0.3, 
                 delta: float = 0.15):
        """
        Args:
            alpha: Visual modality weight (YOLO confidence)
            beta: Chemical modality weight (normalized proxy)
            delta: Conflict detection threshold (|C_YOLO - Ê(t)| > δ)
        """
        assert abs(alpha + beta - 1.0) < 1e-6, "Weights must sum to 1.0"
        self.alpha = alpha
        self.beta = beta
        self.delta = delta
        
    def fuse_single(self, c_yolo: float, e_hat: float, 
                    fruit_type: str = 'unknown') -> Dict:
        """
        Fuse single detection with chemical proxy
        
        Returns:
            Dict with fusion_score, classification, conflict_status, etc.
        """
        # Ensure inputs in [0,1]
        c_yolo = float(np.clip(c_yolo, 0.0, 1.0))
        e_hat = float(np.clip(e_hat, 0.0, 1.0))
        
        # Calculate disagreement
        disagreement = abs(c_yolo - e_hat)
        has_conflict = disagreement > self.delta
        
        # Conflict resolution (Section 3.3.5)
        if has_conflict:
            if c_yolo > e_hat:
                # YOLO dominant (higher confidence in vision)
                # Boost visual weight to 0.9, reduce chemical to 0.1
                F_t = (0.9 * c_yolo) + (0.1 * e_hat)
                resolution = "yolo_dominant"
                resolution_note = "Visual confidence significantly higher, trusting vision"
            else:
                # Chemical proxy surprisingly high but still conservative
                # Moderate boost to chemical (0.4) but keep visual primary (0.6)
                F_t = (0.6 * c_yolo) + (0.4 * e_hat)
                resolution = "chemical_boosted"
                resolution_note = "Chemical indicators elevated, moderate chemical weight applied"
        else:
            # Standard late fusion
            F_t = (self.alpha * c_yolo) + (self.beta * e_hat)
            resolution = "standard_fusion"
            resolution_note = "Modalities agree within threshold"
        
        # Classification using thesis thresholds (Table 3.3.4)
        # Note: These can be overridden per-fruit in batch processing
        classification = self._classify_freshness(F_t)
        
        return {
            'fusion_score': float(F_t),
            'classification': classification,
            'visual_confidence': c_yolo,
            'chemical_proxy': e_hat,
            'has_conflict': has_conflict,
            'disagreement': float(disagreement),
            'conflict_threshold': self.delta,
            'resolution_strategy': resolution,
            'resolution_note': resolution_note,
            'weights_applied': {
                'alpha_visual': 0.9 if (has_conflict and c_yolo > e_hat) else 
                               (0.6 if (has_conflict and c_yolo <= e_hat) else self.alpha),
                'beta_chemical': 0.1 if (has_conflict and c_yolo > e_hat) else 
                                (0.4 if (has_conflict and c_yolo <= e_hat) else self.beta)
            }
        }
    
    def _classify_freshness(self, fusion_score: float) -> str:
        """
        Thesis Table 3.3.4 thresholds:
        Fresh: F(t) ≥ 0.80
        Ripe (Optimal): 0.65 ≤ F(t) < 0.80  
        Overripe/Spoiled: F(t) < 0.65
        """
        if fusion_score >= 0.80:
            return 'Fresh'
        elif fusion_score >= 0.65:
            return 'Ripe'
        else:
            return 'Overripe'
    
    def batch_fuse(self, yolo_results: List[Dict], 
                   chemical_readings: List) -> List[Dict]:
        """
        Batch fusion of YOLO detections with chemical simulations
        
        Args:
            yolo_results: List of detection dicts with 'confidence' and 'fruit_type'
            chemical_readings: List of ChemicalReading dicts or objects
        """
        if len(yolo_results) != len(chemical_readings):
            raise ValueError("Mismatch between detection and chemical counts")
        
        fused_results = []
        
        for i, (yolo_det, chem) in enumerate(zip(yolo_results, chemical_readings)):
            # Extract chemical proxy
            if isinstance(chem, dict):
                e_hat = chem.get('normalized_proxy', 0.5)
                chem_data = chem
            else:
                # Handle dataclass
                e_hat = chem.normalized_proxy
                chem_data = asdict(chem) if hasattr(chem, '__dataclass_fields__') else vars(chem)
            
            # Get fruit type for potential fruit-specific logic
            fruit_type = yolo_det.get('fruit_type', yolo_det.get('class_name', 'unknown'))
            
            # Perform fusion
            fusion_result = self.fuse_single(
                c_yolo=yolo_det.get('confidence', 0),
                e_hat=e_hat,
                fruit_type=fruit_type
            )
            
            # Merge all information
            merged_result = {
                # Original detection data
                'bbox': yolo_det.get('bbox', yolo_det.get('box', [])),
                'fruit_type': fruit_type,
                'yolo_confidence': yolo_det.get('confidence', 0),
                'yolo_class': yolo_det.get('class_name', 'unknown'),
                
                # Fusion results
                **fusion_result,
                
                # Chemical details
                'chemical_data': chem_data,
                
                # Metadata
                'detection_index': i,
                'fusion_method': 'late_fusion_decision_level',
                'fusion_version': '0.7_0.3_with_conflict_resolution',
                'trl_level': 'TRL_3_simulation'
            }
            
            fused_results.append(merged_result)
        
        return fused_results
    
    def get_statistics(self, fused_results: List[Dict]) -> Dict:
        """Calculate aggregate statistics for a batch"""
        if not fused_results:
            return {}
        
        conflicts = sum(1 for r in fused_results if r.get('has_conflict'))
        classifications = {}
        for r in fused_results:
            cls = r.get('classification', 'Unknown')
            classifications[cls] = classifications.get(cls, 0) + 1
        
        return {
            'total_fruits': len(fused_results),
            'conflict_cases': conflicts,
            'conflict_rate': conflicts / len(fused_results),
            'classification_distribution': classifications,
            'average_fusion_score': np.mean([r['fusion_score'] for r in fused_results]),
            'average_visual_conf': np.mean([r['visual_confidence'] for r in fused_results]),
            'average_chemical_proxy': np.mean([r['chemical_proxy'] for r in fused_results])
        }
