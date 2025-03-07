# main.py
import os
import pytesseract

from IA_package.pdf_processor import pdf_para_imagens, imagens_para_texto
from IA_package.rag_processor import realizar_RAG
from IA_package.certificate_extractor import (
    extrair_informacoes_certificados,
    salvar_certificados
)
from IA_package.validator import validar_data
from IA_package.atividades import Atividades

if __name__ == "__main__":
    # Configurações iniciais
    pasta_imagens = "imagens"
    poppler_path = r"C:\Arquivos de Programas\poppler\poppler-24.08.0\Library\bin"
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # Exemplo de dados para processamento
    caminho_pdf = "aluno/210421 - Felipe Pires.pdf"
    nome_aluno = "Felipe Pires dos Santos"
    num_cert = 2
    ra = 210421
    
    # Instância das atividades
    atividades = Atividades  # classe ou dicionário com horas padrão

    # 1. Extrai o texto do PDF
    pdf_para_imagens(caminho_pdf, pasta_imagens, poppler_path)
    texto_dict = imagens_para_texto(pasta_imagens)

    # 2. Realiza o RAG para obter contexto adicional
    query = f"Informações relevantes sobre o certificado de {nome_aluno}"
    contexto_adicional = realizar_RAG(texto_dict, query)
    contexto_formulado = f"Contexto adicional recuperado:\n{contexto_adicional}\n"

    # 3. Extrai as informações dos certificados via modelo
    resultado_modelo = extrair_informacoes_certificados(
        texto_dict,
        num_cert,
        nome_aluno,
        atividades,
        contexto_formulado
    )

    # 4. Salva o resultado em um arquivo JSON
    salvar_certificados(resultado_modelo, "certificados.json")

    # 5. Valida a data do certificado em relação ao RA
    validar_data(ra)

    # Outras validações ou fluxos...
    print("Processo concluído.")
