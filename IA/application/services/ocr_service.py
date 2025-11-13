import os
from typing import Dict, Optional
import pytesseract
from PIL import Image, ImageFilter, ImageOps

class OCRService:

    def __init__(self, teseract_cmd: Optional[str] = None):
        if teseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = teseract_cmd

    def _preprocessar_imagem(self, imagem: Image.Image) -> Image.Image:
        img = imagem.convert("L")
        img = img.filter(ImageFilter.MedianFilter())
        img = ImageOps.invert(img.point(lambda x: 0 if x < 140 else 255, "1"))
        
        if img.width < 1000:
            fator = 1000 / img.width
            nova_altura = int(img.height * fator)
            img = img.resize((1000, nova_altura))

        return img

    def extrair_texto(self, pasta_imagens: str) -> Dict[str, str]:
        textos: Dict[str, str] = {}

        for i, nome_arquivo in enumerate(sorted(os.listdir(pasta_imagens))):
            caminho_imagem = os.path.join(pasta_imagens, nome_arquivo)

            if os.path.isfile(caminho_imagem):
                imagem = Image.open(caminho_imagem)

                imagem_pp = self._preprocessar_imagem(imagem)

                texto = pytesseract.image_to_string(
                    imagem_pp,
                    lang="por+eng" 
                )
                textos[f"texto_{i + 1}"] = texto
        return textos