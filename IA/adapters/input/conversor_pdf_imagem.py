import os
from typing import List
from pdf2image import convert_from_path

class ConversorPDFImagem:
    def __init__(self, poppler_path:str):
        self.poppler_path = poppler_path
        
    