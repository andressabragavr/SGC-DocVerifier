from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

import warnings
warnings.filterwarnings("ignore")

def realizar_RAG(texto_dict, query):
    """
    Realiza o processo de RAG para obter contexto adicional a partir do dicionário de textos.
    
    Parâmetros:
      - texto_dict (dict): Dicionário onde as chaves identificam os textos extraídos de cada página.
      - query (str): Consulta que define qual informação relevante se deseja recuperar.
    
    Retorna:
      - Uma string contendo o contexto concatenado dos trechos mais relevantes.
    """
    # 1. Junta todos os textos extraídos em um único documento
    documento = " ".join(texto_dict.values())
    
    # 2. Divide o documento em pedaços menores (chunks) para facilitar a indexação
    text_splitter = CharacterTextSplitter(separator=" ", chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(documento)
    
    # 3. Cria o vetor de documentos utilizando FAISS e embeddings
    # embeddings = OllamaEmbeddings(model="llama3.3")
    embeddings = OllamaEmbeddings(model="llama3.1")
    vectorstore = FAISS.from_texts(chunks, embeddings)
    
    # 4. Realiza a busca por similaridade para encontrar os trechos mais relevantes para a query
    documentos_relevantes = vectorstore.similarity_search(query, k=3)
    
    # 5. Concatena os trechos encontrados para formar o contexto adicional
    contexto = "\n".join([doc.page_content for doc in documentos_relevantes])
    return contexto
