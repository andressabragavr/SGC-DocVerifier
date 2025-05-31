import os
from typing import Dict
import pytesseract
from PIL import Image

class OCRService:
    
    def __init__ (self, teseract_cmd: str = None):
        
        if teseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = teseract_cmd
        
    