import openai
from openai import OpenAI

class OpenAIAdapter:
    """
    Classe responsável pela integração da API da OpenAI com o sistema
    """
    def __init__(self, api_key):
        """
        Inicializa o adaptador com a chave da API da OpenAI.

        Args:
            api_key (str): Chave da API da OpenAI.
        """
        openai.api_key = api_key
        
    def chat_completion(self, messages: list[dict]) -> str:
        """
        Realiza uma chamada de chat para a API da OpenAI com as mensagens fornecidas.

        Args:
            messages (list[dict]): Lista de mensagens a serem enviadas para o modelo.

        Raises:
            RuntimeError: Se ocorrer um erro ao chamar a API da OpenAI.

        Returns:
            str: Resposta do modelo OpenAI.
        """
        client = OpenAI()
        try:
            response = client.chat.completions.create(
                model = "gpt-4.1",
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Erro na API OpenAI: {str(e)}")
        
        