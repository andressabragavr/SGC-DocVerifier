import os
from typing import List
from pdf2image import convert_from_path

class ConversorPDFImagem:
    def __init__(self, poppler_path:str):
        self.poppler_path = poppler_path
        
    def converter_2_imagens(self, caminho_pdf: str, pasta_destino: str) -> List[str]:
        #Criação da pasta destino
        os.makedirs(pasta_destino, exist_ok = True)
        self._limpar_pasta(pasta_destino)
        
        imagens = convert_from_path(caminho_pdf, poppler_path = self.poppler_path)
        caminhos_imagens = []
        
        for i, imagem in enumerate(imagens):
            caminho_imagem = os.path.join(pasta_destino, f"pagina_{i + 1}.png")
            imagem.save(caminho_imagem, "PNG")
            caminhos_imagens.append(caminho_imagem)
            
        return caminhos_imagens