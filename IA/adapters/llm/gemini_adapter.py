# adapters/llm/gemini_adapter.py
from google import genai

class GeminiAdapter:
    def __init__(self,
                 api_key: str | None = None,
                 model: str = "gemini-2.5-flash",
                 temperature: float = 0.3,
                 max_output_tokens: int = 4096):
        self.client = genai.Client(api_key=api_key)  # se None, lê GEMINI_API_KEY
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def _extract_text(self, resp) -> str:
        # 1) caminho “feliz”
        if getattr(resp, "text", None):
            t = (resp.text or "").strip()
            if t:
                return t
        # 2) fallback manual
        texts = []
        for cand in getattr(resp, "candidates", []) or []:
            content = getattr(cand, "content", None)
            if not content:
                continue
            for p in getattr(content, "parts", []) or []:
                t = getattr(p, "text", None)
                if t is None and isinstance(p, dict):
                    t = p.get("text")
                if t:
                    texts.append(t)
        return "\n".join(texts).strip()

    def chat_completion(self, messages: list[dict]) -> str:
        try:
            # LLMService envia [{"role":"system","content":...}, {"role":"user","content":...}]
            prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)

            # Algumas versões aceitam config=..., outras não. Tentamos e, se der TypeError, re-chamamos sem.
            try:
                resp = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
            except TypeError:
                resp = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )

            saida = self._extract_text(resp)
            if saida:
                return saida

            # Opcional: tornar o erro informativo em vez de retornar vazio silencioso
            finish = [getattr(c, "finish_reason", None) for c in getattr(resp, "candidates", []) or []]
            safety = [getattr(c, "safety_ratings", None) for c in getattr(resp, "candidates", []) or []]
            usage  = getattr(resp, "usage_metadata", None)
            raise RuntimeError(f"Gemini retornou vazio. finish_reason={finish}, safety={safety}, usage={usage}")

        except Exception as e:
            raise RuntimeError(f"Erro na API Gemini: {e}") from e
