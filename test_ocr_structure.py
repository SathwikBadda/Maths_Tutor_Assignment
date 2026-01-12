"""
Test script to understand PaddleOCR output structure
"""
from paddleocr import PaddleOCR
import sys

# Initialize
print("Initializing PaddleOCR...")
import paddle
paddle.set_device('cpu')

ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Test with a sample image
test_image = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"

print(f"\nProcessing: {test_image}")
result = ocr.ocr(test_image)

print(f"\n=== RESULT STRUCTURE ===")
print(f"Type: {type(result)}")
print(f"Length: {len(result) if result else 0}")

if result and len(result) > 0:
    print(f"\nFirst element type: {type(result[0])}")
    print(f"First element length: {len(result[0]) if isinstance(result[0], (list, tuple)) else 'N/A'}")
    
    if isinstance(result[0], list) and len(result[0]) > 0:
        print(f"\n=== FIRST LINE ===")
        print(f"Type: {type(result[0][0])}")
        print(f"Content: {result[0][0]}")
        
        if isinstance(result[0][0], (list, tuple)) and len(result[0][0]) >= 2:
            print(f"\nBBox (element 0): {result[0][0][0]}")
            print(f"Text info (element 1): {result[0][0][1]}")
            print(f"Text info type: {type(result[0][0][1])}")

print(f"\n=== FULL RESULT ===")
import json
try:
    print(json.dumps(result, indent=2, ensure_ascii=False))
except:
    print(result)
