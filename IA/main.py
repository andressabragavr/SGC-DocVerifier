import os
from dotenv import load_dotenv
from application.services.detector_tipo_service import DetectorTipoService
from adapters.input.conversor_pdf_imagem import ConversorPDFImagem
from application.services.ocr_service import OCRService
from application.services.rag_service import contexto_rag
from resources.prompts.carregador_prompt import carregar_prompt_formatado
from resources.atividades import atividades
from adapters.llm.gemini_adapter import GeminiAdapter
from application.services.llm_service import LLMService
from adapters.llm.openai_adapter import OpenAIAdapter 
from application.services.json_service import salvar_resultado_em_json

if __name__ == "__main__":
    load_dotenv()
    
    pasta_imagens = "data/imagens_convertidas/"
    
    # Pedro
    caminho_arquivo = "data/alunos/certificados_Pedro_Lisboa.pdf"
    nome_aluno = "Pedro Henrique Lisboa"
    
    # Andressa
    # caminho_arquivo = "data/alunos/210058 - Andressa Braga.pdf"
    # caminho_arquivo = "data/alunos/CursoHTML, CSS e Boostrap5 -ANDRESSA.pdf"
    # nome_aluno = "Andressa Braga Vieira Rodrigues"
    
    poppler_path = r"C:\Arquivos de Programas\poppler\poppler-24.08.0\Library\bin"
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    # Detector MIME
    detector = DetectorTipoService()
    tipo = detector.detectar_tipo_arquivo(caminho_arquivo)
    
    # Conersão tipos
    if tipo == "pdf":
        conversor = ConversorPDFImagem(poppler_path = poppler_path)
        conversor.converter_2_imagens(caminho_pdf = caminho_arquivo, pasta_destino = pasta_imagens)
    else:
        os.makedirs(pasta_imagens, exist_ok = True)
        destino = os.path.join(pasta_imagens, "pagina_1.png")
        os.system(f"copy {caminho_arquivo} {destino}")
        
    # OCR
    ocr = OCRService(teseract_cmd = tesseract_path)
    textos_extraidos = ocr.extrair_texto(pasta_imagens)
    num_cert = len(textos_extraidos)
    
    # RAG
    texto_completo = "\n".join(textos_extraidos.values())
    contexto = contexto_rag(texto_completo, query = "Extração de informações do certificado")
        
    # Prompt
    prompt_formatado = carregar_prompt_formatado(
        "resources/prompts/base_prompt.txt",
        texto_dict = textos_extraidos,
        num_cert = num_cert,
        nome_aluno = nome_aluno,
        atividades = str(atividades),
        contexto = contexto
    )
    
    # Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    adapter = GeminiAdapter(api_key=gemini_api_key)
    
    # OpenAI
    # openai_api_key = os.getenv("OPENAI_API_KEY")
    # adapter = OpenAIAdapter(api_key=openai_api_key)
    
    servico_llm = LLMService(adapter)
    resposta = servico_llm.obter_resposta(prompt_formatado, contexto=contexto)
    
    arquivo = salvar_resultado_em_json(resposta, "resultado_certificado")
    
    print("Finalizado")