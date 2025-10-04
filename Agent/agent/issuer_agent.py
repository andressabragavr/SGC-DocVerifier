# === MODO GRATUITO (sem LLM) ===============================================
from ddgs import DDGS
from rapidfuzz import fuzz
from urllib.parse import urlparse
import os, re
from typing import Dict, Any

TOOL_TAG = "unknown"
_ISSUER_AGENT = None

_WHITELIST_HINTS = ("institucional", "sobre", "história", "quem somos", "about")
_BLACKLIST_DOMAINS = ("pt.stackoverflow.com", "br.quora.com", "reddit.com", "brainly.com", "yahoo.com")

def _norm(s: str) -> str:
    s = (s or "").lower().strip()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9áéíóúâêôãõç\s\-_.:/]", " ", s))

def _score_result(query_norm: str, title: str, snippet: str, url: str, year_hint: str | None = None) -> float:
    host = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    title_n = _norm(title); snip_n = _norm(snippet)

    s_title = fuzz.token_set_ratio(query_norm, title_n)
    s_snip  = fuzz.token_set_ratio(query_norm, snip_n)
    base = max(s_title, s_snip) / 100.0  # 0..1

    bonus = 0.0
    # oficiais
    if host.endswith(".edu.br") or host.endswith(".gov.br"):
        bonus += 0.15
    # eventos/associações (.org.br) + keywords
    if host.endswith(".org.br"):
        bonus += 0.08
    if "sbc.org.br" in host or "ihc" in host:
        bonus += 0.07
    if any(h in title_n or h in snip_n for h in _WHITELIST_HINTS):
        bonus += 0.05
    # ano no caminho corresponde ao ano do certificado
    if year_hint and year_hint in path:
        bonus += 0.05

    malus = 0.0
    if any(bad in host for bad in _BLACKLIST_DOMAINS):
        malus += 0.15

    score = max(0.0, min(1.0, base + bonus - malus))
    return score

def issuer_verify_free(instituicao: str, year_hint: str | None = None) -> Dict[str, Any]:
    q = instituicao.strip()
    if not q:
        return {"valido": None, "confianca": 0.0, "evidencias": [], "fonte": "duck-free"}

    query_norm = _norm(q)
    evid_raw = []
    with DDGS() as ddg:
        # 2 rodadas de busca para melhorar recall
        queries = [q, f"{q} site oficial", f"{q} instituição", f"{q} universidade", f"{q} evento"]
        seen = set()
        for qq in queries:
            for r in ddg.text(qq, region="br-pt", max_results=8):  # gratuito
                url = r.get("href") or r.get("url") or ""
                title = r.get("title") or ""
                snippet = r.get("body") or r.get("snippet") or ""
                if not url or url in seen: 
                    continue
                seen.add(url)
                sc = _score_result(query_norm, title, snippet, url, year_hint=year_hint)
                evid_raw.append({
                    "titulo": (title or url)[:180],
                    "url": url[:400],
                    "score": sc
                })

    evid_sorted = sorted(evid_raw, key=lambda x: x["score"], reverse=True)
    top = evid_sorted[:3]
    best = top[0]["score"] if top else 0.0

    # regra de decisão simples:
    # >=0.85 => verified; 0.75–0.85 => weak; <0.75 => not_found
    valido = True if best >= 0.85 else (None if best >= 0.75 else False)
    conf = float(round(best, 3))

    return {
        "valido": valido,
        "confianca": conf,
        "evidencias": [{"titulo": e["titulo"], "url": e["url"]} for e in top],
        "fonte": "duck-free"
    }
# ===========================================================================

# Ajuste leve em issuer_verify: escolha o modo free quando quiser (ex.: por ENV)
def issuer_verify(instituicao: str, year_hint: str | None = None) -> Dict[str, Any]:
    if os.getenv("EMISSOR_FORCE_FREE", "0") == "1" or not os.getenv("OPENAI_API_KEY"):
        return issuer_verify_free(instituicao, year_hint=year_hint)
    try:
        return _issuer_verify_llm(instituicao)  # LLM não usa year_hint
    except Exception:
        return issuer_verify_free(instituicao, year_hint=year_hint)

# extraia o corpo atual de issuer_verify (que usa AgentExecutor) para:
def _issuer_verify_llm(instituicao: str) -> Dict[str, Any]:
    global _ISSUER_AGENT, TOOL_TAG
    _ISSUER_AGENT = _ISSUER_AGENT or _build_agent()
    user_input = (
        f'Instituição: "{instituicao}"\n'
        "Instruções: Pesquise e traga de 1 a 3 evidências confiáveis (título + URL). "
        "Considere variações do nome e siglas. No final, responda SOMENTE o JSON com as chaves "
        '"valido", "confianca" e "evidencias" (lista de objetos com campos "titulo" e "url").'
    )
    result = _ISSUER_AGENT.invoke({"input": user_input})
    raw = (result.get("output", "") or "")
    data = _safe_parse_json(raw) or {}
    valido = data.get("valido", None)
    conf = float(data.get("confianca", 0.0) or 0.0)
    evid = data.get("evidencias", [])
    out_evid = []
    for e in evid:
        t = str(e.get("titulo", ""))[:180]
        u = str(e.get("url", ""))[:400]
        if u:
            out_evid.append({"titulo": t or u, "url": u})
    return {
        "valido": valido if valido in [True, False, None] else None,
        "confianca": conf if 0.0 <= conf <= 1.0 else 0.0,
        "evidencias": out_evid[:3],
        "fonte": f"llm+{TOOL_TAG}",
    }