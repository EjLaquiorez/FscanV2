"""
YOLO Detector module for fruit detection
"""
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import yaml
from typing import List, Dict, Tuple, Optional


class YOLODetector:
    """YOLO-based fruit detector"""
    
    def __init__(self, model_path: str, data_yaml_path: str, confidence_threshold: float = 0.25, iou_threshold: float = 0.45):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to YOLO model weights (.pt file)
            data_yaml_path: Path to data.yaml file with class names
            confidence_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
        """
        self.model_path = Path(model_path)
        self.data_yaml_path = Path(data_yaml_path)
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        
        # Load model
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model = YOLO(str(self.model_path))
        
        # Load class names from data.yaml (override model's class names)
        self.class_names = self._load_class_names()
        
        # Override model's class names with our custom names
        if self.class_names:
            # Update the model's names attribute if it exists
            if hasattr(self.model, 'names'):
                # Convert our dict to list format if needed, or keep as dict
                for class_id, class_name in self.class_names.items():
                    if isinstance(self.model.names, dict):
                        self.model.names[class_id] = class_name
                    elif isinstance(self.model.names, list):
                        if class_id < len(self.model.names):
                            self.model.names[class_id] = class_name
        
        print(f"YOLO detector loaded with {len(self.class_names)} classes")
        if len(self.class_names) > 0:
            print(f"Class names: {list(self.class_names.values())[:5]}..." if len(self.class_names) > 5 else f"Class names: {list(self.class_names.values())}")
    
    def _load_class_names(self) -> Dict[int, str]:
        """Load class names from data.yaml"""
        try:
            if not self.data_yaml_path.exists():
                print(f"Warning: data.yaml not found at {self.data_yaml_path}, using default class names")
                return self._get_default_class_names()
            
            with open(self.data_yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data:
                    print(f"Warning: data.yaml is empty, using default class names")
                    return self._get_default_class_names()
                
                names = data.get('names', {})
                if not names:
                    print(f"Warning: No 'names' key found in data.yaml, using default class names")
                    return self._get_default_class_names()
                
                # Convert to integer keys if they're strings
                class_names = {}
                for key, value in names.items():
                    try:
                        class_id = int(key)
                        class_names[class_id] = str(value).strip()
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Invalid class entry '{key}: {value}', skipping: {e}")
                        continue
                
                if not class_names:
                    print(f"Warning: No valid class names loaded, using default class names")
                    return self._get_default_class_names()
                
                print(f"Successfully loaded {len(class_names)} class names from {self.data_yaml_path}")
                return class_names
                
        except Exception as e:
            print(f"Warning: Could not load class names from {self.data_yaml_path}: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return self._get_default_class_names()
    
    def _get_default_class_names(self) -> Dict[int, str]:
        """Return default class names based on Fruit_dataset (15 classes)"""
        return {
            0: 'Banana Unripe',
            1: 'Banana Ripe',
            2: 'Banana Overripe',
            3: 'Mango Unripe',
            4: 'Mango Ripe',
            5: 'Mango Overripe',
            6: 'Cashew Unripe',
            7: 'Cashew Ripe',
            8: 'Cashew Overripe',
            9: 'Cacao Unripe',
            10: 'Cacao Ripe',
            11: 'Cacao Overripe',
            12: 'Pineapple Unripe',
            13: 'Pineapple Ripe',
            14: 'Pineapple Overripe'
        }
    
    def detect(self, image_path: str) -> List[Dict]:
        """
        Detect fruits in an image
        
        Args:
            image_path: Path to input image
            
        Returns:
            List of detection results with bounding boxes, classes, and confidence scores
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Run inference
        results = self.model.predict(
            source=image_path,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False
        )
        
        # Parse results
        detections = []
        if len(results) > 0:
            result = results[0]
            
            # Get boxes, classes, and confidences
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for i in range(len(boxes)):
                    box = boxes[i]
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get class ID and confidence
                    class_id = int(box.cls[0].cpu().numpy())
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    # Get class name - ensure we always get a proper name
                    class_name = self.class_names.get(class_id)
                    if class_name is None:
                        # Try to get from model's names if available
                        if hasattr(self.model, 'names') and self.model.names:
                            if isinstance(self.model.names, dict):
                                class_name = self.model.names.get(class_id, f"Class_{class_id}")
                            elif isinstance(self.model.names, list) and class_id < len(self.model.names):
                                class_name = self.model.names[class_id]
                            else:
                                class_name = f"Class_{class_id}"
                        else:
                            class_name = f"Class_{class_id}"
                        print(f"Warning: Class ID {class_id} not found in class_names, using: {class_name}")
                    
                    # Determine quality status and ripeness from class name
                    quality_status, ripeness = self._parse_quality_status(class_name)
                    
                    # Extract fruit type (remove ripeness from class name)
                    fruit_type = self._extract_fruit_type(class_name)
                    
                    detection = {
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'class_id': class_id,
                        'class_name': class_name,
                        'fruit_type': fruit_type,  # Just the fruit name (e.g., "Pineapple", "Banana")
                        'confidence': confidence,
                        'quality_status': quality_status,  # unripe, ripe, overripe
                        'ripeness': ripeness  # Unripe, Ripe, Overripe
                    }
                    
                    detections.append(detection)
        
        return detections
    
    def _parse_quality_status(self, class_name: str) -> Tuple[str, str]:
        """
        Parse quality status and ripeness from class name
        New format: "{Fruit} {Ripeness}" (e.g., "Banana Unripe", "Mango Ripe")
        
        Args:
            class_name: Name of the detected class
            
        Returns:
            Tuple of (quality_status, ripeness)
        """
        class_lower = class_name.lower()
        
        # Extract fruit type and ripeness level
        # Format is: "{Fruit} {Ripeness}" or old format variations
        parts = class_name.split()
        
        # Determine ripeness from class name
        if 'unripe' in class_lower:
            ripeness = 'Unripe'
            quality_status = 'unripe'
        elif 'overripe' in class_lower or 'over-ripe' in class_lower:
            ripeness = 'Overripe'
            quality_status = 'overripe'
        elif 'ripe' in class_lower:
            # Check if it's "half-ripe" or just "ripe"
            if 'half-ripe' in class_lower or 'half ripe' in class_lower:
                ripeness = 'Half-Ripe'
                quality_status = 'ripe'
            else:
                ripeness = 'Ripe'
                quality_status = 'ripe'
        elif 'rotten' in class_lower:
            ripeness = 'Overripe'  # Treat rotten as overripe
            quality_status = 'rotten'
        elif 'fresh' in class_lower:
            ripeness = 'Ripe'  # Treat fresh as ripe
            quality_status = 'fresh'
        else:
            ripeness = 'Unknown'
            quality_status = 'unknown'
        
        return quality_status, ripeness
    
    def _extract_fruit_type(self, class_name: str) -> str:
        """
        Extract just the fruit type from class name, removing ripeness level
        Format: "{Fruit} {Ripeness}" -> "{Fruit}"
        
        Args:
            class_name: Full class name (e.g., "Pineapple Unripe", "Banana Ripe", "Mango Overripe")
            
        Returns:
            Fruit type only (e.g., "Pineapple", "Banana", "Mango")
        """
        import re
        
        # List of ripeness keywords (order matters - check longer/compound words first)
        ripeness_keywords = ['overripe', 'over-ripe', 'half-ripe', 'half ripe', 'underripe', 'unripe', 'ripe', 'rotten', 'fresh']
        
        # Split the class name into parts
        parts = class_name.split()
        
        if len(parts) < 2:
            # Single word, return as is
            return class_name
        
        # Check if the last part matches a ripeness keyword (case-insensitive)
        last_part_lower = parts[-1].lower()
        
        # Check for exact match or if last part contains a ripeness keyword
        matched_keyword = None
        for keyword in ripeness_keywords:
            if last_part_lower == keyword or keyword in last_part_lower:
                matched_keyword = keyword
                break
        
        if matched_keyword:
            # Last part is a ripeness keyword, remove it and return the rest
            fruit_type = ' '.join(parts[:-1]).strip()
            return fruit_type
        
        # If last part doesn't match, try to find and remove ripeness keyword from anywhere
        class_lower = class_name.lower()
        for keyword in ripeness_keywords:
            if keyword in class_lower:
                # Remove the keyword and any surrounding spaces
                pattern = r'\s+' + re.escape(keyword) + r'\s*$'  # At end with space before
                fruit_type = re.sub(pattern, '', class_name, flags=re.IGNORECASE)
                if fruit_type != class_name:
                    return fruit_type.strip()
                
                pattern = r'^\s*' + re.escape(keyword) + r'\s+'  # At start with space after
                fruit_type = re.sub(pattern, '', class_name, flags=re.IGNORECASE)
                if fruit_type != class_name:
                    return fruit_type.strip()
                
                pattern = r'\s+' + re.escape(keyword) + r'\s+'  # In middle with spaces
                fruit_type = re.sub(pattern, ' ', class_name, flags=re.IGNORECASE)
                if fruit_type != class_name:
                    return fruit_type.strip()
        
        # Fallback: if no keyword found, assume last part is ripeness and remove it
        return ' '.join(parts[:-1]).strip() if len(parts) > 1 else class_name
    
    def save_annotated_image(self, input_path: str, output_path: str, detections: List[Dict]) -> None:
        """
        Save image with bounding box annotations
        
        Args:
            input_path: Path to input image
            output_path: Path to save annotated image
            detections: List of detection results
        """
        # Read image
        image = cv2.imread(input_path)
        if image is None:
            raise ValueError(f"Could not read image: {input_path}")
        
        # Draw bounding boxes
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            quality_status = detection['quality_status']
            
            # Convert to integers
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Choose color based on quality status
            color_map = {
                'fresh': (0, 255, 0),      # Green
                'ripe': (255, 255, 0),      # Yellow
                'unripe': (0, 255, 255),    # Cyan
                'overripe': (0, 165, 255),  # Orange
                'rotten': (0, 0, 255),      # Red
                'unknown': (128, 128, 128)  # Gray
            }
            color = color_map.get(quality_status, (128, 128, 128))
            
            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label
            label = f"{class_name} {confidence:.2f}"
            
            # Calculate text size
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            
            # Draw label background
            cv2.rectangle(
                image,
                (x1, y1 - text_height - baseline - 5),
                (x1 + text_width, y1),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                image,
                label,
                (x1, y1 - baseline - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
        
        # Save annotated image
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image)
    
    def get_class_names(self) -> Dict[int, str]:
        """Get dictionary of class ID to class name mappings"""
        return self.class_names.copy()

