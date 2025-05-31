import os

from application.services.detector_tipo_service import DetectorTipoService
from adapters.input.conversor_pdf_imagem import ConversorPDFImagem

if __name__ == "__main__":
    
    pasta_imagens = "data/imagens_convertidas/"
    caminho_arquivo = "data/alunos/210421 - Felipe Pires.pdf"
    
    poppler_path = r"C:\Arquivos de Programas\poppler\poppler-24.08.0\Library\bin"
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    # Detector MIME
    detector = DetectorTipoService()
    tipo = detector.detectar_tipo_arquivo(caminho_arquivo)
    print(f"Tipo de arquivo detectado: {tipo}")
    
    # Conersão tipos
    if tipo == "pdf":
        conversor = ConversorPDFImagem(poppler_path = poppler_path)
        conversor.converter_2_imagens(caminho_pdf = caminho_arquivo, pasta_destino = pasta_imagens)
    else:
        os.makedirs(pasta_imagens, exist_ok = True)
        destino = os.path.join(pasta_imagens, "pagina_1.png")
        os.system(f"copy {caminho_arquivo} {destino}")
        
    