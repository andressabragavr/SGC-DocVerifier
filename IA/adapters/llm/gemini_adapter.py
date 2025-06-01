import google.generativeai as genai

class GeminiAdapter:
    """
    Classe responsável pela integração da API do Gemini com o sistema
    """
    def __init__(self, api_key):
        """
        Inicializa o adaptador com a chave da API do Gemini.

        Args:
            api_key (str): Chave da API do Gemini.
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def chat_completion(self, mensagens: list[dict]) -> str:
        """
        Realiza uma chamada de chat para a API do Gemini com as mensagens fornecidas.

        Args:
            mensagens (list[dict]): Lista de mensagens a serem enviadas para o modelo.

        Raises:
            RuntimeError: Se ocorrer um erro ao chamar a API do Gemini.

        Returns:
            str: Resposta do modelo Gemini como uma string.
        """
        try:
            # Concatena as mensagens
            prompt = "\n".join([msg["content"] for msg in mensagens])

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.5,
                    "max_output_tokens": 1000
                }
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Erro na API Gemini: {str(e)}")