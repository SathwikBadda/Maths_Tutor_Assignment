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
        self.config = config
        self.logger = logging.getLogger("ocr_processor")

        # Force PaddleOCR to use CPU explicitly BEFORE initialization
        import paddle
        paddle.set_device('cpu')
        
        # Initialize PaddleOCR with minimal parameters to avoid conflicts
        # Note: use_gpu parameter is not available in all versions
        # CPU mode is enforced via paddle.set_device('cpu') above
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=config.get('use_angle_cls', True),
                lang=config.get('lang', 'en')
            )
            self.logger.info("OCR processor initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize OCR: {e}")
            # Fallback: try with absolute minimal config
            self.ocr = PaddleOCR(lang='en')
            self.logger.warning("OCR initialized with fallback minimal config")

        self.confidence_threshold = config.get('confidence_threshold', 0.8)

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

            # Run OCR - DO NOT pass cls parameter, it's handled by use_angle_cls in init
            result = self.ocr.ocr(image_path)
            
            # Debugging log
            self.logger.info(f"OCR result type: {type(result)}")
            if isinstance(result, list) and len(result) > 0:
                self.logger.info(f"OCR result len: {len(result)}, first element type: {type(result[0])}")

            # Handle None or empty results
            if result is None or len(result) == 0:
                self.logger.warning("OCR returned empty result")
                return self._empty_response()

            # Get the lines from the first image
            lines = result[0]
            
            # Check if we got any text
            if not lines or (isinstance(lines, list) and len(lines) == 0):
                self.logger.warning("OCR found no text in image")
                return self._empty_response()

            # Parse the results
            blocks = []
            all_text = []
            confidences = []

            for line in lines:
                try:
                    # Defensive unpacking - handle different structures
                    if not isinstance(line, (list, tuple)) or len(line) < 2:
                        self.logger.warning(f"Skipping malformed line: {line}")
                        continue
                    
                    bbox = line[0]
                    text_conf = line[1]
                    
                    # text_conf should be [text, confidence]
                    if not isinstance(text_conf, (list, tuple)) or len(text_conf) < 2:
                        self.logger.warning(f"Skipping malformed text_conf: {text_conf}")
                        continue
                        
                    text = str(text_conf[0])
                    confidence = float(text_conf[1])

                    blocks.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": bbox
                    })

                    all_text.append(text)
                    confidences.append(confidence)
                    
                except Exception as line_error:
                    self.logger.warning(f"Error parsing line: {line_error}")
                    continue

            # Build response
            if not all_text:
                return self._empty_response()
                
            return self._build_response(blocks, all_text, confidences)

        except TypeError as te:
            self.logger.error(f"TypeError during OCR processing: {te}", exc_info=True)
            return self._error_response(f"OCR TypeError: {te}")
        except Exception as e:
            self.logger.error(f"OCR processing failed: {str(e)}", exc_info=True)
            return self._error_response(str(e))

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

            # Run OCR - DO NOT pass cls parameter
            result = self.ocr.ocr(image_array)

            # Debugging log
            self.logger.info(f"OCR result type (bytes): {type(result)}")

            if result is None or len(result) == 0:
                self.logger.warning("OCR returned empty result (bytes)")
                return self._empty_response()

            lines = result[0]
            
            if not lines:
                self.logger.warning("OCR found no text in image (bytes)")
                return self._empty_response()
            
            # Parse results
            blocks = []
            all_text = []
            confidences = []

            for line in lines:
                try:
                    if not isinstance(line, (list, tuple)) or len(line) < 2:
                        continue
                    
                    bbox = line[0]
                    text_conf = line[1]
                    
                    if not isinstance(text_conf, (list, tuple)) or len(text_conf) < 2:
                        continue
                        
                    text = str(text_conf[0])
                    confidence = float(text_conf[1])

                    blocks.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": bbox
                    })

                    all_text.append(text)
                    confidences.append(confidence)
                    
                except Exception:
                    continue

            if not all_text:
                return self._empty_response()
                
            return self._build_response(blocks, all_text, confidences)

        except Exception as e:
            self.logger.error(f"OCR processing failed: {str(e)}", exc_info=True)
            return self._error_response(str(e))

    def _build_response(self, blocks, all_text, confidences):
        """Build successful response dictionary."""
        full_text = " ".join(all_text)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        low_confidence = avg_confidence < self.confidence_threshold

        self.logger.info(
            f"OCR completed: {len(blocks)} blocks, "
            f"avg confidence: {avg_confidence:.3f}"
        )

        return {
            "text": full_text,
            "confidence": avg_confidence,
            "low_confidence": low_confidence,
            "blocks": blocks,
            "error": None
        }

    def _empty_response(self):
        """Return empty response when no text found."""
        return {
            "text": "",
            "confidence": 0.0,
            "low_confidence": True,
            "blocks": [],
            "error": None
        }

    def _error_response(self, error_msg):
        """Return error response."""
        return {
            "text": "",
            "confidence": 0.0,
            "low_confidence": True,
            "blocks": [],
            "error": error_msg
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