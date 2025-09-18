# Agent/agent/issuer_agent.py
import os, json, re
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ===================== Tools =====================
TOOL_TAG = "unknown"

def make_search_tool():
    """
    Tenta Tavily (pacote novo). Se não houver chave ou falhar, cai para DuckDuckGo.
    Requisitos:
      - Tavily: pip install -U langchain-tavily
      - DuckDuckGo: pip install duckduckgo-search
    """
    global TOOL_TAG
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        try:
            from langchain_tavily import TavilySearch
            TOOL_TAG = "tavily"
            return TavilySearch(max_results=5, api_key=tavily_key)
        except Exception:
            pass
    from langchain_community.tools import DuckDuckGoSearchResults
    TOOL_TAG = "duck"
    return DuckDuckGoSearchResults(max_results=5)

# ===================== Prompt =====================
SYSTEM = """Você é um verificador de instituições emissoras de certificados no Brasil.
TAREFA: Dado APENAS o NOME da instituição, pesquise e responda um JSON com:
- valido: true|false|null
- confianca: número entre 0 e 1 (ex.: 0.85)
- evidencias: lista de objetos com campos 'titulo' e 'url'

REGRAS:
- NUNCA invente link. Somente use URLs reais dos resultados que você encontrou.
- Se houver dúvida forte (muitos nomes parecidos ou poucos sinais oficiais), responda "valido": null e "confianca": 0.0.
- Fontes que aumentam confiança: domínios .edu.br, .gov.br, site oficial, página "Sobre"/"Institucional", MEC/e-MEC.
- Evite blogs e fóruns como fonte principal. Se usar, marque baixa confiança.
- Saída FINAL deve ser APENAS o JSON pedido, sem texto extra.
"""

# IMPORTANTe:
# Use SOMENTE as variáveis exigidas pelo create_react_agent:
# {tools}, {tool_names}, {input}, {agent_scratchpad}
PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     SYSTEM +
     "\n\nFerramentas disponíveis:\n{tools}\n"
     "Você só pode usar estas ferramentas: {tool_names}."
    ),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

_ISSUER_AGENT: AgentExecutor | None = None

def _build_agent() -> AgentExecutor:
    llm = ChatOpenAI(model=os.getenv("AGENT_LLM_MODEL", "gpt-4o-mini"), temperature=0, timeout=20)
    tool = make_search_tool()
    agent = create_react_agent(llm, [tool], PROMPT)
    # verbose=True ajuda a depurar (Thought -> Action -> Observation)
    return AgentExecutor(agent=agent, tools=[tool], verbose=True, handle_parsing_errors=True)

def _safe_parse_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        pass
    # tenta capturar o último bloco { ... }
    for cand in re.findall(r"\{[\s\S]*\}", text)[::-1]:
        try:
            return json.loads(cand)
        except Exception:
            continue
    return {}

def issuer_verify(instituicao: str) -> Dict[str, Any]:
    """Retorna: {valido, confianca, evidencias[], fonte}"""
    if not os.getenv("OPENAI_API_KEY"):
        return {"valido": None, "confianca": 0.0, "evidencias": [], "fonte": "sem-llm"}

    global _ISSUER_AGENT, TOOL_TAG
    _ISSUER_AGENT = _ISSUER_AGENT or _build_agent()

    try:
        # Monte TODO o pedido do usuário em UMA string e passe apenas como 'input'
        user_input = (
            f'Instituição: "{instituicao}"\n'
            "Instruções: Pesquise e traga de 1 a 3 evidências confiáveis (título + URL). "
            "Considere variações do nome e siglas. No final, responda SOMENTE o JSON com as chaves "
            '"valido", "confianca" e "evidencias" (lista de objetos com campos "titulo" e "url").'
        )

        result = _ISSUER_AGENT.invoke({"input": user_input})
        raw = result.get("output", "") or ""
        data = _safe_parse_json(raw) or {}

        valido = data.get("valido", None)
        conf = float(data.get("confianca", 0.0) or 0.0)
        evid = data.get("evidencias", [])

        # Sanitiza evidências
        out_evid: List[Dict[str, str]] = []
        for e in evid:
            t = str(e.get("titulo", ""))[:180]
            u = str(e.get("url", ""))[:400]
            if u:
                out_evid.append({"titulo": t or u, "url": u})

        return {
            "valido": valido if valido in [True, False, None] else None,
            "confianca": conf if 0.0 <= conf <= 1.0 else 0.0,
            "evidencias": out_evid[:3],
            "fonte": f"llm+{TOOL_TAG}"
        }
    except Exception as e:
        return {"valido": None, "confianca": 0.0, "evidencias": [], "fonte": f"erro_agente:{e}"}
