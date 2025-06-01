class LLMService:
    """
    Classe que realiza a comunicação com a LLM, para poder obter a resposta com base no que foi passado.
    """
    def __init__(self, llm_adapter):
        """
        Inicializa o serviço LLM com o adaptador fornecido.

        Args:
            llm_adapter (object): Adaptador para a LLM, responsável por gerenciar as chamadas à API da LLM.
        """
        self.llm_adapter = llm_adapter

    def obter_resposta(self, pergunta: str, contexto: str = "") -> str:
        """
        Obtém uma resposta da LLM com base na pergunta e no contexto fornecidos.

        Args:
            pergunta (str): Pergunta realizada para a IA
            contexto (str, optional): Contexto gerado pela RAG. Defaults to "".

        Returns:
            str: Resposta da LLM.
        """
        mensagens = []
        if contexto:
            mensagens.append({"role": "system", "content": f"Contexto: {contexto}"})
        mensagens.append({"role": "user", "content": pergunta})

        return self.llm_adapter.chat_completion(mensagens)