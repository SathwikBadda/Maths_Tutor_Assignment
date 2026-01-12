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

        # Initialize PaddleOCR
        self.ocr = PaddleOCR(
            use_angle_cls=config.get('use_angle_cls', True),
            lang=config.get('lang', 'en'),
           
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
            # NOTE: Removed cls=True as it causes TypeError in some versions/environments
            # where it conflicts with internal predict() arguments.
            # Angle classification is enabled via init parameter `use_angle_cls=True`.
            result = self.ocr.ocr(image_path)
            
            # Debugging log
            self.logger.info(f"OCR result type: {type(result)}")
            if isinstance(result, list):
                self.logger.info(f"OCR result len: {len(result)}")
                if len(result) > 0:
                     self.logger.info(f"First element type: {type(result[0])}")

            # PaddleOCR returns a list of results (one per image)
            # Structure typically: [ [ [box, [text, conf]], ... ], ... ]
            if result is None or len(result) == 0:
                self.logger.warning("OCR returned empty result")
                return self._empty_response()

            # Handle different return structures
            # sometimes result is [[line1, line2]] -> result[0] is the lines
            # sometimes result is [line1, line2] directly (rare but possible in old versions)
            
            lines = result[0]
            if isinstance(lines, list) and len(lines) == 0:
                 self.logger.warning("OCR found no text in image (empty list)")
                 return self._empty_response()
                 
            # Fallback if result[0] is not a list of lines but a line itself? 
            # (Unlikely given PaddleOCR 2.x standard, but safety first)
            if not isinstance(lines, list) and lines is not None:
                # This implies result structure mismatch, verify nesting
                 self.logger.warning(f"Unexpected result[0] type: {type(lines)}")
                 return self._empty_response()

            if lines is None:
                self.logger.warning("OCR found no text in image (None)")
                return self._empty_response()

            blocks = []
            all_text = []
            confidences = []

            for line in lines:
                # Defensive unpacking
                if not isinstance(line, (list, tuple)) or len(line) < 2:
                    self.logger.warning(f"Skipping malformed line: {line}")
                    continue
                
                bbox = line[0]
                text_conf = line[1]
                
                if not isinstance(text_conf, (list, tuple)) or len(text_conf) < 2:
                    self.logger.warning(f"Skipping malformed text_conf: {text_conf}")
                    continue
                    
                text = text_conf[0]
                confidence = text_conf[1]

                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })

                all_text.append(text)
                confidences.append(confidence)

            return self._build_response(blocks, all_text, confidences)

        except TypeError as te:
             self.logger.error(f"TypeError during OCR processing: {te}. Trying to handle...", exc_info=True)
             return self._error_response(te)
        except Exception as e:
            self.logger.error(f"OCR processing failed: {str(e)}", exc_info=True)
            return self._error_response(e)

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
            # NOTE: Removed cls=True to fix TypeError consistency
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
            
            # Same parsing logic
            blocks = []
            all_text = []
            confidences = []

            for line in lines:
                if not isinstance(line, (list, tuple)) or len(line) < 2:
                    continue
                bbox = line[0]
                text_conf = line[1]
                if not isinstance(text_conf, (list, tuple)) or len(text_conf) < 2:
                    continue
                text = text_conf[0]
                confidence = text_conf[1]

                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })

                all_text.append(text)
                confidences.append(confidence)

            return self._build_response(blocks, all_text, confidences)

        except Exception as e:
            self.logger.error(f"OCR processing failed: {str(e)}", exc_info=True)
            return self._error_response(e)

    def _build_response(self, blocks, all_text, confidences):
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

    def _empty_response(self):
        return {
            "text": "",
            "confidence": 0.0,
            "low_confidence": True,
            "blocks": [],
            "error": None
        }

    def _error_response(self, e):
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