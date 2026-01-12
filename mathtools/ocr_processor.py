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
    Stable for Streamlit deployment.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("ocr_processor")

        # ✅ Force CPU (MANDATORY for Streamlit)
        paddle.set_device("cpu")

        # ✅ Enable angle_cls safely
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=config.get("lang", "en")
        )

        self.confidence_threshold = config.get("confidence_threshold", 0.8)
        self.logger.info("OCR processor initialized (CPU, angle_cls enabled)")

    # ----------------------------------------------------

    def process_image(self, image_path: str) -> Dict[str, Any]:
        try:
            self.logger.info(f"Processing image: {image_path}")

            result = self.ocr.ocr(image_path)

            if not result or not result[0]:
                return self._empty_response()

            blocks, all_text, confidences = [], [], []

            for line in result[0]:
                # ✅ SAFE parsing (FIX)
                bbox = line[0]
                text = line[1][0]
                confidence = line[1][1]

                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })

                all_text.append(text)
                confidences.append(confidence)

            return self._build_response(blocks, all_text, confidences)

        except Exception as e:
            self.logger.error("OCR processing failed", exc_info=True)
            return self._error_response(e)

    # ----------------------------------------------------

    def process_image_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)

            result = self.ocr.ocr(image_array)

            if not result or not result[0]:
                return self._empty_response()

            blocks, all_text, confidences = [], [], []

            for line in result[0]:
                bbox = line[0]
                text = line[1][0]
                confidence = line[1][1]

                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })

                all_text.append(text)
                confidences.append(confidence)

            return self._build_response(blocks, all_text, confidences)

        except Exception as e:
            self.logger.error("OCR processing failed", exc_info=True)
            return self._error_response(e)

    # ----------------------------------------------------
    # Helpers
    # ----------------------------------------------------

    def _build_response(self, blocks, all_text, confidences):
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
    # result = processor.process_image("path/to/math_problem.jpg")
    # print(result)