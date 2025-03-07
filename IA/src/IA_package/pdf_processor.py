import os
import pytesseract
from pdf2image import convert_from_path

import warnings
warnings.filterwarnings("ignore")

def pdf_para_imagens(caminho_pdf, pasta_imagens, poppler_path):
    """
    Converte um arquivo PDF em imagens e salva cada página como uma imagem PNG na pasta especificada.
    
    Parâmetros:
    - caminho_pdf (str): Caminho completo do arquivo PDF.
    - pasta_imagens (str): Caminho da pasta onde as imagens serão salvas.
    - poppler_path (str): Caminho para o executável Poppler, necessário para o pdf2image.
    """
    
    # Cria a pasta "imagens" se ela não existir
    if not os.path.exists(pasta_imagens):
        os.makedirs(pasta_imagens)
    
    # Limpa os arquivos da pasta "imagens" antes de começar
    for nome_arquivo in os.listdir(pasta_imagens):
        caminho_arquivo = os.path.join(pasta_imagens, nome_arquivo)
        if os.path.isfile(caminho_arquivo):
            os.remove(caminho_arquivo)
    
    # Converte o PDF em imagens e salva na pasta "imagens"
    imagens = convert_from_path(caminho_pdf, poppler_path=poppler_path)
    for i, imagem in enumerate(imagens):
        caminho_imagem = os.path.join(pasta_imagens, f"pagina_{i + 1}.png")
        imagem.save(caminho_imagem, "PNG")
        
def imagens_para_texto(pasta_imagem):
    """
    Processa as imagens em uma pasta, aplica OCR para extrair o texto e salva em arquivos .txt.
    
    Parâmetros:
    - pasta_imagem (str): Caminho da pasta onde as imagens estão localizadas.
    - pasta_texto (str): Caminho da pasta onde os arquivos .txt serão salvos.
    """
    
    dicionario_textos = {}
    
    # Opcional: ordenar os nomes dos arquivos para garantir a ordem das páginas
    for i, nome_arquivo in enumerate(sorted(os.listdir(pasta_imagem))):
        caminho_imagem = os.path.join(pasta_imagem, nome_arquivo)
        if os.path.isfile(caminho_imagem):
            resultado = pytesseract.image_to_string(caminho_imagem)
            chave = f"texto_{i + 1}"
            dicionario_textos[chave] = resultado
    
    return dicionario_textos
