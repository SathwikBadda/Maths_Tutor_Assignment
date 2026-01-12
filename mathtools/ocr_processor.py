from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
from typing import Dict, Any
import logging
import io
import paddle


class OCRProcessor:
    """
    OCR processor using PaddleOCR for extracting text from images.
    Specialized for mathematical notation.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("ocr_processor")

        # 🔥 FIX 1: Disable angle classifier (causes PaddleX std::exception)
        self.ocr = PaddleOCR(
            use_angle_cls=False,   # ✅ CRITICAL FIX
            lang=config.get('lang', 'en')
        )

        # Force CPU (already correct)
        paddle.set_device('cpu')
        self.logger.info(f"PaddlePaddle device: {paddle.get_device()}")

        self.confidence_threshold = config.get('confidence_threshold', 0.8)
        self.logger.info("OCR processor initialized")

    def _load_image(self, image_path: str) -> np.ndarray:
        """Safely load image as numpy array."""
        image = Image.open(image_path).convert("RGB")
        return np.array(image)

    def process_image(self, image_path: str) -> Dict[str, Any]:
        try:
            self.logger.info(f"Processing image: {image_path}")

            # 🔥 FIX 2: Always pass numpy array to PaddleOCR
            image_array = self._load_image(image_path)
            result = self.ocr.ocr(image_array)

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
                bbox = line[0]
                text, confidence = line[1]

                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })

                all_text.append(text)
                confidences.append(confidence)

            full_text = " ".join(all_text)
            avg_confidence = sum(confidences) / len(confidences)
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

    def process_image_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_array = np.array(image)

            result = self.ocr.ocr(image_array)

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
                bbox = line[0]
                text, confidence = line[1]

                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })

                all_text.append(text)
                confidences.append(confidence)

            full_text = " ".join(all_text)
            avg_confidence = sum(confidences) / len(confidences)
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