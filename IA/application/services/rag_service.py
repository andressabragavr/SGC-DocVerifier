from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter

def contexto_rag(
    texto: str, 
    query: str, 
    chunk_size: int = 500,
    chunck_overlap: int = 100,
    k: int = 3
    ) -> str:
    
    """
    Função que utiliza o modelo de embeddings do HuggingFace para criar um contexto relevante

    Returns:
        str: Contexto relevante para a query fornecida, baseado no texto dado.
    """
    
    embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L12-v2")
    
    splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = chunk_size,
        chunk_overlap = chunck_overlap,
    )
    
    chunks = splitter.split_text(texto)
    
    vector_store = FAISS.from_texts(chunks, embedding = embeddings)
    
    docs_relavntes = vector_store.similarity_search(query, k = k)
    
    contexto = "\n".join([
        doc.page_content if hasattr(doc, 'page_content') else str(doc)
        for doc in docs_relavntes
    ])
    
    return contexto