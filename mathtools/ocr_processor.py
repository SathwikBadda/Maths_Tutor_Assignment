from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
from typing import Dict, Any, List, Tuple
import logging
import io

class OCRProcessor:
    """
    OCR processor using PaddleOCR for extracting text from images.
    Specialized for mathematical notation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OCR processor.
        
        Args:
            config: OCR configuration from config.yaml
        """
        self.config = config
        self.logger = logging.getLogger("ocr_processor")
        
        # Initialize PaddleOCR
        self.ocr = PaddleOCR(
            use_angle_cls=config.get('use_angle_cls', True),
            lang=config.get('lang', 'en'),
            
            show_log=False
        )
        
        # Force PaddleOCR to use CPU explicitly
        import paddle
        paddle.set_device('cpu')
        
        # Debugging: Log PaddlePaddle device
        self.logger.info(f"PaddlePaddle device: {paddle.get_device()}")
        
        self.confidence_threshold = config.get('confidence_threshold', 0.8)
        
        self.logger.info("OCR processor initialized")
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image and extract text with confidence scores.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            self.logger.info(f"Processing image: {image_path}")
            
            # Run OCR
            result = self.ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                self.logger.warning("No text detected in image")
                return {
                    "text": "",
                    "confidence": 0.0,
                    "low_confidence": True,
                    "blocks": [],
                    "error": None
                }
            
            # Extract text and confidence
            blocks = []
            all_text = []
            confidences = []
            
            for line in result[0]:
                bbox, (text, confidence) = line
                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })
                all_text.append(text)
                confidences.append(confidence)
            
            # Combine text
            full_text = " ".join(all_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Check if confidence is below threshold
            low_confidence = avg_confidence < self.confidence_threshold
            
            self.logger.info(
                f"OCR completed: {len(blocks)} blocks, "
                f"avg confidence: {avg_confidence:.3f}, "
                f"low_confidence: {low_confidence}"
            )
            
            return {
                "text": full_text,
                "confidence": avg_confidence,
                "low_confidence": low_confidence,
                "blocks": blocks,
                "error": None
            }
        
        except Exception as e:
            self.logger.error(f"OCR processing failed: {str(e)}", exc_info=True)
            return {
                "text": "",
                "confidence": 0.0,
                "low_confidence": True,
                "blocks": [],
                "error": str(e)
            }
    
    def process_image_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process image from bytes.
        
        Args:
            image_bytes: Image data as bytes
        
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Convert bytes to numpy array
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
            
            # Run OCR
            result = self.ocr.ocr(image_array, cls=True)
            
            # Process results (same logic as process_image)
            if not result or not result[0]:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "low_confidence": True,
                    "blocks": [],
                    "error": None
                }
            
            blocks = []
            all_text = []
            confidences = []
            
            for line in result[0]:
                bbox, (text, confidence) = line
                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })
                all_text.append(text)
                confidences.append(confidence)
            
            full_text = " ".join(all_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            low_confidence = avg_confidence < self.confidence_threshold
            
            return {
                "text": full_text,
                "confidence": avg_confidence,
                "low_confidence": low_confidence,
                "blocks": blocks,
                "error": None
            }
        
        except Exception as e:
            self.logger.error(f"OCR processing failed: {str(e)}", exc_info=True)
            return {
                "text": "",
                "confidence": 0.0,
                "low_confidence": True,
                "blocks": [],
                "error": str(e)
            }
    
    def enhance_math_text(self, text: str) -> str:
        """
        Post-process OCR text to fix common math notation issues.
        
        Args:
            text: Raw OCR text
        
        Returns:
            Enhanced text
        """
        # Common OCR mistakes in math
        replacements = {
            'х': 'x',  # Cyrillic x
            'у': 'y',  # Cyrillic y
            'О': '0',  # Letter O to zero
            '|': '1',  # Pipe to one (in some contexts)
            'l': '1',  # Lowercase L to one (in some contexts)
        }
        
        enhanced = text
        for old, new in replacements.items():
            enhanced = enhanced.replace(old, new)
        
        return enhanced


# Example usage
if __name__ == "__main__":
    config = {
        'use_angle_cls': True,
        'lang': 'en',
        'use_gpu': False,
        'confidence_threshold': 0.8
    }
    
    processor = OCRProcessor(config)
    # result = processor.process_image("path/to/math_problem.jpg")
    # print(result)