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
        
        # Try multiple initialization strategies
        init_success = False
        
        # Strategy 1: With angle classification
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=config.get('use_angle_cls', True),
                lang=config.get('lang', 'en')
            )
            self.logger.info("OCR processor initialized successfully with angle_cls")
            init_success = True
        except Exception as e:
            self.logger.warning(f"Failed to initialize OCR with angle_cls: {e}")
        
        # Strategy 2: Without angle classification (more stable on some systems)
        if not init_success:
            try:
                self.ocr = PaddleOCR(
                    use_angle_cls=False,
                    lang='en'
                )
                self.logger.info("OCR initialized without angle_cls (fallback)")
                init_success = True
            except Exception as e:
                self.logger.warning(f"Failed to initialize OCR without angle_cls: {e}")
        
        # Strategy 3: Absolute minimal config
        if not init_success:
            try:
                self.ocr = PaddleOCR(lang='en')
                self.logger.info("OCR initialized with minimal config (last resort)")
                init_success = True
            except Exception as e:
                self.logger.error(f"All OCR initialization strategies failed: {e}")
                raise RuntimeError("Could not initialize PaddleOCR. Check system dependencies.")

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
            # Wrap in try-catch to handle potential std::exception from C++ code
            try:
                result = self.ocr.ocr(image_path)
            except Exception as ocr_error:
                self.logger.error(f"PaddleOCR internal error: {type(ocr_error).__name__}: {ocr_error}")
                # Try to provide helpful error message
                error_msg = str(ocr_error)
                if "std::exception" in error_msg or "exception" in error_msg.lower():
                    return self._error_response(
                        "OCR engine error. This may be due to missing system libraries. "
                        "Please ensure all dependencies are installed."
                    )
                return self._error_response(f"OCR failed: {error_msg}")
            
            # Debugging log
            self.logger.info(f"OCR result type: {type(result)}")
            if isinstance(result, list) and len(result) > 0:
                self.logger.info(f"OCR result len: {len(result)}, first element type: {type(result[0])}")

            # Handle None or empty results
            if result is None or len(result) == 0:
                self.logger.warning("OCR returned empty result")
                return self._empty_response()

            # Get the lines from the first image
            # Handle different return types from PaddleOCR
            lines = result[0]
            
            # CRITICAL: Handle OCRResult object type (newer PaddleOCR versions)
            # Check if result[0] is an OCRResult object
            if hasattr(lines, '__class__') and 'OCRResult' in lines.__class__.__name__:
                self.logger.info(f"Detected OCRResult object, extracting data...")
                
                # Log all available attributes for debugging
                attrs = [attr for attr in dir(lines) if not attr.startswith('_')]
                self.logger.info(f"OCRResult attributes: {attrs}")
                
                # Try multiple possible attributes to extract the data
                extracted = False
                
                # Try 1: rec_res (recognition results)
                if hasattr(lines, 'rec_res') and lines.rec_res is not None:
                    lines = lines.rec_res
                    self.logger.info(f"Extracted from rec_res: {type(lines)}, len={len(lines) if isinstance(lines, list) else 'N/A'}")
                    extracted = True
                
                # Try 2: dt_polys + rec_text + rec_score (separate attributes) - MOST LIKELY FOR CLOUD
                elif hasattr(lines, 'rec_text') and hasattr(lines, 'rec_score'):
                    # Build lines from separate attributes
                    rec_texts = getattr(lines, 'rec_text', [])
                    rec_scores = getattr(lines, 'rec_score', [])
                    dt_polys = getattr(lines, 'dt_polys', [])
                    
                    self.logger.info(f"Building from separate attrs: {len(rec_texts)} texts, {len(rec_scores)} scores, {len(dt_polys)} boxes")
                    
                    # Construct the expected format: [[bbox, (text, score)], ...]
                    new_lines = []
                    for i in range(len(rec_texts)):
                        bbox = dt_polys[i] if i < len(dt_polys) else [[0,0],[0,0],[0,0],[0,0]]
                        text = rec_texts[i] if i < len(rec_texts) else ""
                        score = rec_scores[i] if i < len(rec_scores) else 0.0
                        new_lines.append([bbox, (text, score)])
                    
                    lines = new_lines
                    self.logger.info(f"Constructed {len(lines)} lines from OCRResult attributes")
                    extracted = True
                
                # Try 3: Check for data or results attribute
                elif hasattr(lines, 'data'):
                    lines = lines.data
                    self.logger.info(f"Extracted from data attribute: {type(lines)}")
                    extracted = True
                elif hasattr(lines, 'results'):
                    lines = lines.results
                    self.logger.info(f"Extracted from results attribute: {type(lines)}")
                    extracted = True
                
                # DO NOT use list() conversion - it creates strings!
                
                if not extracted:
                    self.logger.error(f"Could not extract data from OCRResult. Available attrs: {attrs}")
                    if hasattr(lines, '__dict__'):
                        self.logger.error(f"OCRResult __dict__: {lines.__dict__}")
                    return self._empty_response()
            
            # CRITICAL: Validate that lines is actually a list of OCR results
            # Sometimes result[0] might be None or a dict
            if lines is None:
                self.logger.warning("OCR result[0] is None")
                return self._empty_response()
            
            if not isinstance(lines, list):
                self.logger.error(f"OCR result[0] is not a list! Type: {type(lines)}")
                # Log available attributes for debugging
                if hasattr(lines, '__dict__'):
                    self.logger.error(f"Object attributes: {lines.__dict__}")
                return self._empty_response()
            
            if len(lines) == 0:
                self.logger.warning("OCR found no text in image (empty list)")
                return self._empty_response()

            # Parse the results
            blocks = []
            all_text = []
            confidences = []

            # Debug: inspect first line structure
            if len(lines) > 0:
                first_line = lines[0]
                self.logger.info(f"First line structure: {first_line}")
                self.logger.info(f"First line type: {type(first_line)}, len: {len(first_line) if isinstance(first_line, (list, tuple)) else 'N/A'}")

            for idx, line in enumerate(lines):
                try:
                    # PaddleOCR returns: [[bbox_points], (text, confidence)]
                    # where bbox_points is a list of 4 coordinate pairs
                    
                    if not isinstance(line, (list, tuple)):
                        self.logger.warning(f"Line {idx} is not list/tuple: {type(line)}")
                        continue
                    
                    if len(line) < 2:
                        self.logger.warning(f"Line {idx} has insufficient elements: {len(line)}")
                        continue
                    
                    bbox = line[0]
                    text_info = line[1]
                    
                    # Debug first few lines
                    if idx < 3:
                        self.logger.info(f"Line {idx} - bbox type: {type(bbox)}, text_info type: {type(text_info)}, text_info: {text_info}")
                    
                    # text_info should be (text, confidence) tuple
                    if isinstance(text_info, (list, tuple)):
                        if len(text_info) >= 2:
                            text = str(text_info[0])
                            confidence = float(text_info[1])
                        elif len(text_info) == 1:
                            # Sometimes only text is returned
                            text = str(text_info[0])
                            confidence = 1.0
                        else:
                            self.logger.warning(f"Line {idx} text_info is empty")
                            continue
                    elif isinstance(text_info, str):
                        # Direct string
                        text = text_info
                        confidence = 1.0
                    else:
                        self.logger.warning(f"Line {idx} text_info unexpected type: {type(text_info)}")
                        continue

                    # Skip empty text
                    if not text or text.strip() == "":
                        continue

                    blocks.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": bbox
                    })

                    all_text.append(text)
                    confidences.append(confidence)
                    
                except Exception as line_error:
                    self.logger.error(f"Error parsing line {idx}: {line_error}", exc_info=True)
                    continue

            self.logger.info(f"Parsed {len(all_text)} text blocks from {len(lines)} lines")

            # Build response
            if not all_text:
                self.logger.warning("No text extracted after parsing all lines")
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
            # Wrap in try-catch to handle potential std::exception from C++ code
            try:
                result = self.ocr.ocr(image_array)
            except Exception as ocr_error:
                self.logger.error(f"PaddleOCR internal error (bytes): {type(ocr_error).__name__}: {ocr_error}")
                error_msg = str(ocr_error)
                if "std::exception" in error_msg or "exception" in error_msg.lower():
                    return self._error_response(
                        "OCR engine error. This may be due to missing system libraries."
                    )
                return self._error_response(f"OCR failed: {error_msg}")

            # Debugging log
            self.logger.info(f"OCR result type (bytes): {type(result)}")

            if result is None or len(result) == 0:
                self.logger.warning("OCR returned empty result (bytes)")
                return self._empty_response()

            lines = result[0]
            
            # Handle OCRResult object type (same comprehensive handling as process_image)
            if hasattr(lines, '__class__') and 'OCRResult' in lines.__class__.__name__:
                self.logger.info(f"Detected OCRResult object (bytes), extracting data...")
                attrs = [attr for attr in dir(lines) if not attr.startswith('_')]
                self.logger.info(f"OCRResult attributes (bytes): {attrs}")
                
                extracted = False
                
                if hasattr(lines, 'rec_res') and lines.rec_res is not None:
                    lines = lines.rec_res
                    self.logger.info(f"Extracted from rec_res (bytes): {type(lines)}")
                    extracted = True
                elif hasattr(lines, 'rec_text') and hasattr(lines, 'rec_score'):
                    rec_texts = getattr(lines, 'rec_text', [])
                    rec_scores = getattr(lines, 'rec_score', [])
                    dt_polys = getattr(lines, 'dt_polys', [])
                    
                    new_lines = []
                    for i in range(len(rec_texts)):
                        bbox = dt_polys[i] if i < len(dt_polys) else [[0,0],[0,0],[0,0],[0,0]]
                        text = rec_texts[i] if i < len(rec_texts) else ""
                        score = rec_scores[i] if i < len(rec_scores) else 0.0
                        new_lines.append([bbox, (text, score)])
                    
                    lines = new_lines
                    self.logger.info(f"Constructed {len(lines)} lines from OCRResult (bytes)")
                    extracted = True
                elif hasattr(lines, 'data'):
                    lines = lines.data
                    self.logger.info(f"Extracted from data attribute (bytes): {type(lines)}")
                    extracted = True
                elif hasattr(lines, 'results'):
                    lines = lines.results
                    self.logger.info(f"Extracted from results attribute (bytes): {type(lines)}")
                    extracted = True
                
                if not extracted:
                    self.logger.error(f"Could not extract data from OCRResult (bytes). Attrs: {attrs}")
                    return self._empty_response()
            
            if not lines:
                self.logger.warning("OCR found no text in image (bytes)")
                return self._empty_response()
            
            if not isinstance(lines, list):
                self.logger.error(f"Lines is not a list (bytes)! Type: {type(lines)}")
                return self._empty_response()
            
            # Parse results
            blocks = []
            all_text = []
            confidences = []

            for idx, line in enumerate(lines):
                try:
                    if not isinstance(line, (list, tuple)):
                        continue
                    
                    if len(line) < 2:
                        continue
                    
                    bbox = line[0]
                    text_info = line[1]
                    
                    # text_info should be (text, confidence) tuple
                    if isinstance(text_info, (list, tuple)):
                        if len(text_info) >= 2:
                            text = str(text_info[0])
                            confidence = float(text_info[1])
                        elif len(text_info) == 1:
                            text = str(text_info[0])
                            confidence = 1.0
                        else:
                            continue
                    elif isinstance(text_info, str):
                        text = text_info
                        confidence = 1.0
                    else:
                        continue

                    # Skip empty text
                    if not text or text.strip() == "":
                        continue

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