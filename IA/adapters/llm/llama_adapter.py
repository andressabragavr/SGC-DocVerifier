# adapters/llm/llama_adapter.py
# pip install ollama

from typing import List, Dict, Optional
import ollama


class LlamaAdapter:
    """
    Adapter para Llama via Ollama local (sem LangChain).
    Interface: chat_completion(List[Dict]) -> str
    """

    def __init__(
        self,
        model: str = "llama3.2:1b",
        host: str = "http://localhost:11434",
        temperature: float = 0.3,
        max_tokens: Optional[int] = 1000,
        num_ctx: int = 4096,
    ):
        self.client = ollama.Client(host=host)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.num_ctx = num_ctx

    def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
        """
        try:
            options = {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
            }
            if self.max_tokens is not None:
                options["num_predict"] = self.max_tokens  # ~ max_tokens

            resp = self.client.chat(
                model=self.model,
                messages=messages,
                options=options,
            )
            return resp["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Erro na API Llama (Ollama): {str(e)}")
