import os
from typing import List
from pdf2image import convert_from_path

class ConversorPDFImagem:
    """
    Classe para converter arquivos PDF em imagens PNG.
    Salva cada página do PDF como uma imagem PNG em uma pasta especificada.
    """
    
    def __init__(self, poppler_path:str):
        """
        Inicializa o conversor com o caminho do executável Poppler.

        Args:
            poppler_path (str): Caminho para o executável Poppler, necessário para o pdf2image.
        """
        self.poppler_path = poppler_path
        
    def converter_2_imagens(self, caminho_pdf: str, pasta_destino: str) -> List[str]:
        """
        Converte um arquivo PDF em imagens PNG, salva cada página na pasta especificada.

        Args:
            caminho_pdf (str): Caminho completo do arquivo PDF.
            pasta_destino (str): Pasta onde as imagens serão salvas.

        Returns:
            List[str]: Lista com caminho das imagens geradas.
        """
        
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
    
    def _limpar_pasta(self, pasta: str) -> None:
        """
        Função auxiliar que remove todos os arquivos dentro da pasta especificada.

        Args:
            pasta (str): Caminho da pasta a ser limpa.
        """
        for arquivo in os.listdir(pasta):
            caminho = os.path.join(pasta, arquivo)
            if os.path.isfile(caminho):
                os.remove(caminho)