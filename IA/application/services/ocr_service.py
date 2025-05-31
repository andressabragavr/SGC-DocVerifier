import os
from typing import Dict
import pytesseract
from PIL import Image

class OCRService:
    
    def __init__ (self, teseract_cmd: str = None):
        
        if teseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = teseract_cmd
        
    def extrair_texto(self, pasta_imagens: str) -> Dict[str, str]:
        
        textos = {}
        
        for i, nome_arquivo in enumerate(sorted(os.listdir(pasta_imagens))):
            caminho_imagem = os.path.join(pasta_imagens, nome_arquivo)
            
            if os.path.isfile(caminho_imagem):
                imagem = Image.open(caminho_imagem)
                texto = pytesseract.image_to_string(imagem)
                textos[f"texto_{i + 1}"] = texto
                
        return textos