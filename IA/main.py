import os
import sys
import json
from dotenv import load_dotenv
from application.services.detector_tipo_service import DetectorTipoService
from adapters.input.conversor_pdf_imagem import ConversorPDFImagem
from application.services.ocr_service import OCRService
from application.services.rag_service import contexto_rag
from resources.prompts.carregador_prompt import carregar_prompt_formatado
from resources.atividades import atividades
from adapters.llm.gemini_adapter import GeminiAdapter
from adapters.llm.llama_adapter import LlamaAdapter
from application.services.llm_service import LLMService
from adapters.llm.openai_adapter import OpenAIAdapter 
from application.services.json_service import salvar_resultado_em_json
from application.services.dataset_logger import build_record, append_jsonl
import json, uuid

if __name__ == "__main__":
    load_dotenv()
    
    pasta_imagens = "../IA/data/imagens_convertidas"
    
    # RECEBIMENTO DE ARGUMENTOS DO BACKEND
    if len(sys.argv) < 3:
        print(json.dumps({"erro": "Parâmetros insuficientes: <caminho_arquivo> <nome_aluno> <ra_aluno> <curso_aluno>"}))
        sys.exit(1)

    caminho_arquivo = sys.argv[1]
    nome_aluno = sys.argv[2]
    ra_aluno = sys.argv[3]
    curso_aluno = sys.argv[4]

    # VERIFICAÇÃO DE EXISTÊNCIA
    if not os.path.exists(caminho_arquivo):
        print(json.dumps({"erro": f"Arquivo não encontrado: {caminho_arquivo}"}))
        sys.exit(1)
    
    poppler_path = r"C:\Program Files\poppler\poppler-24.08.0\Library\bin"
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
    prompt_path = os.path.join(os.path.dirname(__file__), "resources", "prompts", "base_prompt.txt")
    
    prompt_formatado = carregar_prompt_formatado(
        prompt_path,
        texto_dict = textos_extraidos,
        num_cert = num_cert,
        nome_aluno = nome_aluno,
        atividades = str(atividades),
        contexto = contexto
    )
    
    # Gemini
    # gemini_api_key = os.getenv("GEMINI_API_KEY")
    # adapter = GeminiAdapter(api_key=gemini_api_key)
    
    # OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    adapter = OpenAIAdapter(api_key=openai_api_key)
    
    # Llama
    # adapter = LlamaAdapter()
    
    servico_llm = LLMService(adapter)
    resposta = servico_llm.obter_resposta(prompt_formatado, contexto=contexto)
    
    arquivo = salvar_resultado_em_json(resposta, "resultado_certificado")
    
    # 2) prepara dados pro dataset
    ocr_text = "\n".join(textos_extraidos.values())
    cert_id = f"{os.path.splitext(os.path.basename(caminho_arquivo))[0]}-{uuid.uuid4().hex[:6]}"

    try:
        llm_json = json.loads(resposta)
    except Exception:
        # se a LLM veio com cercas ```json, seu json_service já trata no arquivo;
        # aqui tentamos limpar rapidamente para o dataset também:
        txt = resposta.strip()
        if txt.startswith("```json"):
            txt = txt[7:]
        if txt.endswith("```"):
            txt = txt[:-3]
        llm_json = json.loads(txt)

    # 3) constrói o registro no formato mínimo e grava
    record = build_record(
        cert_id=cert_id,
        hint_nome_aluno=nome_aluno,
        hint_curso_aluno=curso_aluno,
        inscricao_aluno_ano = 2000 + int(''.join(filter(str.isdigit, ra_aluno))[:2]),
        ocr_text=ocr_text,
        llm_json=llm_json,
    )
    append_jsonl(record)  # grava em data/gold/gold.jsonl
    
    print(resposta)