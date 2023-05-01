from paddleocr import PaddleOCR

try:
    PaddleOCR(use_angle_cls=True, lang="en", show_log=False, debug=False)
except ValueError:
    pass
