import os
from typing import Dict
import pytesseract
from PIL import Image

class OCRService:
    """
    Classe responsável pelo OCR nas imagens.
    """
    def __init__ (self, teseract_cmd: str = None):
        """
        Inicializa o serviço de OCR com o caminho do executável Tesseract, se fornecido.

        Args:
            teseract_cmd (str, optional): Caminho para o executável Tesseract OCR. Defaults to None.
        """
        if teseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = teseract_cmd
        
    def extrair_texto(self, pasta_imagens: str) -> Dict[str, str]:
        """
        Extrai texto de todas as imagens em uma pasta usando OCR.

        Args:
            pasta_imagens (str): Caminho da pasta contendo as imagens.

        Returns:
            Dict[str, str]: Dicionário onde as chaves são nomes de arquivos e os valores são os textos extraídos.
        """
        textos = {}
        
        for i, nome_arquivo in enumerate(sorted(os.listdir(pasta_imagens))):
            caminho_imagem = os.path.join(pasta_imagens, nome_arquivo)
            
            if os.path.isfile(caminho_imagem):
                imagem = Image.open(caminho_imagem)
                texto = pytesseract.image_to_string(imagem)
                textos[f"texto_{i + 1}"] = texto
                
        return textos