from __future__ import annotations
from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime, timezone
from rapidfuzz import fuzz
from agent import client
import os

H_MIN = int(float(os.getenv("H_MIN", "10")))
SIM_ALUNO = int(float(os.getenv("SIM_ALUNO", "92")))
SIM_DUP_FRACA = int(float(os.getenv("SIM_DUP_FRACA", "88")))
REQUIRE_EMISSOR_VALIDO = False  # você não usa CNPJ/site por enquanto
EMISSOR_CACHE_CONF_MIN = float(os.getenv("EMISSOR_CACHE_CONF_MIN", "0.7"))

W_INSTIT, W_NOME, W_DATA, W_HORAS = 40, 30, 20, 10  # pesos

class ValState(TypedDict, total=False):
    cert_id: str
    dados_raw: Dict[str, Any]
    dados: Dict[str, Any]
    emissor: Dict[str, Any]
    checks: Dict[str, bool]
    duplicidade: Dict[str, Any]
    status: str
    justificativa: str
    evidencias: List[Dict[str, Any]]
    erros: List[str]

def _norm(s: Optional[str]) -> str:
    return " ".join(str(s or "").strip().split())

def _iso_date(d: Any) -> Optional[str]:
    if not d: return None
    try:
        s = str(d)
        return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc).date().isoformat()
    except Exception:
        return None

def _sim_nome(a: str, b: str) -> int:
    return fuzz.token_set_ratio(_norm(a).lower(), _norm(b).lower())

def _score_dup(ref: Dict[str, Any], cand: Dict[str, Any]) -> int:
    s_inst = fuzz.token_set_ratio(_norm(ref.get("instituicao")), _norm(cand.get("instituicao")))
    s_nome = _sim_nome(ref.get("nomeNoCertificado",""), cand.get("nomeNoCertificado",""))
    s_data = 100 if _iso_date(ref.get("dataConclusao")) == _iso_date(cand.get("dataConclusao")) else 0
    s_hora = 100 if int(ref.get("horasAtribuidas") or 0) == int(cand.get("horasAtribuidas") or 0) else 0
    total = (s_inst*W_INSTIT + s_nome*W_NOME + s_data*W_DATA + s_hora*W_HORAS) / (W_INSTIT+W_NOME+W_DATA+W_HORAS)
    return int(round(total))

# -------- nós --------
def entrada_prisma(s: ValState) -> ValState:
    s["dados_raw"] = client.get_cert(s["cert_id"])
    return s

def padronizar(s: ValState) -> ValState:
    c = s["dados_raw"]
    s["dados"] = {
        "id": c.get("id"),
        "userName": c.get("user",{}).get("name",""),
        "userRa": c.get("user",{}).get("ra",""),
        "instituicao": _norm(c.get("instituicao")),
        "nomeNoCertificado": _norm(c.get("nomeNoCertificado")),
        "dataConclusao": _iso_date(c.get("dataConclusao")),
        "horasAtribuidas": int(c.get("horasAtribuidas") or 0),
        "fileHashSHA256": c.get("fileHashSHA256"),
        "titulo": _norm(c.get("titulo")),
        "tipoAtividade": _norm(c.get("tipoAtividade")),
        "urlPDF": c.get("urlPDF")
    }
    s.setdefault("evidencias", []).append({"tipo":"padronizacao"})
    return s

def verificar_emissor(s: ValState) -> ValState:
    """
    Passos:
      1) Se não houver nome da instituição -> indefinido.
      2) Tenta ler do cache (Prisma/Issuer). Se trustLevel >= EMISSOR_CACHE_CONF_MIN, usa e retorna.
      3) Se houver OPENAI_API_KEY, chama mini-agente LLM p/ buscar pelo nome e retorna JSON {valido, confianca, evidencias}.
         - Caso melhore a confiança, faz upsert no cache.
      4) Se nada disso, deixa indefinido (MVP).
    """
    inst = (s["dados"].get("instituicao") or "").strip()
    if not inst:
        s["emissor"] = {"valido": None, "confianca": 0.0, "fonte": "sem-instituicao", "evidencias": []}
        s.setdefault("evidencias", []).append({"tipo": "emissor", "resultado": s["emissor"]})
        return s

    # ---------- 2) CACHE (opcional) ----------
    cache = None
    try:
        # Só tenta se seu client tiver esses helpers (não quebra se não tiver)
        if hasattr(client, "get_issuer"):
            cache = client.get_issuer(inst)  # espera {name, isTrusted, trustLevel, ...} ou None
    except Exception:
        cache = None

    if cache:
        trust = float(cache.get("trustLevel") or 0.0)
        is_trusted = bool(cache.get("isTrusted"))
        if trust >= EMISSOR_CACHE_CONF_MIN:
            s["emissor"] = {
                "valido": is_trusted,
                "confianca": trust,
                "fonte": "cache",
                "evidencias": []  # opcionalmente poderia guardar 1 url em 'notes' no cache
            }
            s.setdefault("evidencias", []).append({"tipo": "emissor", "resultado": s["emissor"]})
            return s  # cache forte já resolve

    # ---------- 3) LLM (opcional) ----------
    use_llm = bool(os.getenv("OPENAI_API_KEY"))
    if use_llm:
        try:
            from agent.issuer_agent import issuer_verify  # mini-agente ReAct com tool de busca
            r = issuer_verify(inst)  # -> {"valido": T|F|None, "confianca": 0..1, "evidencias": [{titulo,url}], "fonte":"llm+tavily"}
        except Exception as e:
            r = {"valido": None, "confianca": 0.0, "evidencias": [], "fonte": f"erro_agente:{e}"}
    else:
        r = {"valido": None, "confianca": 0.0, "evidencias": [], "fonte": "sem-llm"}

    # monta resultado no estado
    s["emissor"] = {
        "valido": r.get("valido"),
        "confianca": float(r.get("confianca") or 0.0),
        "fonte": r.get("fonte") or ("llm" if use_llm else "mvp"),
        "evidencias": r.get("evidencias", [])[:3]
    }
    s.setdefault("evidencias", []).append({"tipo": "emissor", "resultado": s["emissor"]})

    # ---------- opcional: atualizar cache com o que a LLM achou ----------
    try:
        if hasattr(client, "upsert_issuer"):
            # só grava se houver algum sinal
            tl = float(s["emissor"]["confianca"])
            itrust = bool(s["emissor"]["valido"]) if s["emissor"]["valido"] is not None else (tl >= EMISSOR_CACHE_CONF_MIN)
            notes = None
            if s["emissor"]["evidencias"]:
                # guarda a 1ª evidência (url) em notes p/ referência rápida
                notes = s["emissor"]["evidencias"][0].get("url")

            client.upsert_issuer({
                "name": inst,
                "isTrusted": itrust,
                "trustLevel": tl,
                "notes": notes
            })
    except Exception:
        pass

    return s


def validar_regras_ies(s: ValState) -> ValState:
    d = s["dados"]
    hoje = datetime.utcnow().date().isoformat()
    horas_ok  = d["horasAtribuidas"] >= H_MIN
    datas_ok  = (d["dataConclusao"] is not None) and (d["dataConclusao"] <= hoje)
    aluno_ok  = _sim_nome(d.get("nomeNoCertificado",""), d.get("userName","")) >= SIM_ALUNO
    formato_ok = bool(d.get("titulo")) and bool(d.get("tipoAtividade"))
    s["checks"] = dict(horas_ok=horas_ok, datas_ok=datas_ok, aluno_ok=aluno_ok, formato_ok=formato_ok)
    ev = s.setdefault("evidencias", [])
    ev += [
        {"tipo":"regra","campo":"horas","ok":horas_ok,"valor":d["horasAtribuidas"],"minimo":H_MIN},
        {"tipo":"regra","campo":"dataConclusao","ok":datas_ok,"valor":d["dataConclusao"],"ate":hoje},
        {"tipo":"regra","campo":"aluno","ok":aluno_ok},
        {"tipo":"regra","campo":"formato","ok":formato_ok},
    ]
    return s

def anti_duplicidade(s: ValState) -> ValState:
    d = s["dados"]
    fortes = client.get_dup_fortes(d.get("fileHashSHA256"), exclude_id=d.get("id"))
    confirmada = len(fortes) > 0

    matches, suspeita = [], False
    if not confirmada:
        q = {
            "instituicao": d.get("instituicao") or "",
            "nome": d.get("nomeNoCertificado") or "",
            "data": d.get("dataConclusao") or "",
            "horas": str(d.get("horasAtribuidas") or "")
        }
        candidatos = client.get_similares(q)
        for c in candidatos:
            if c.get("id") == d.get("id"):
                continue
            score = _score_dup(d, c)
            if score >= SIM_DUP_FRACA:
                suspeita = True
            matches.append({"id": c.get("id"), "score": score})

    s["duplicidade"] = {
        "confirmada": confirmada,
        "suspeita": suspeita,
        "matches": sorted(matches, key=lambda x: -x["score"])[:10]
    }

    ev = s.setdefault("evidencias", [])
    if confirmada:
        ev.append({"tipo": "duplicidade", "modo": "hash"})
    elif suspeita:
        ev.append({"tipo": "duplicidade", "modo": "similaridade", "top": s["duplicidade"]["matches"][:3]})
    else:
        ev.append({"tipo": "duplicidade", "modo": "analise", "resultado": "sem_suspeita"})

    return s

def decidir_status(s: ValState) -> ValState:
    dups   = s["duplicidade"]
    checks = s["checks"]
    em     = s["emissor"]

    # 1) duplicata forte -> RECUSADO
    if dups.get("confirmada"):
        s["status"] = "RECUSADO"
        s["justificativa"] = "Duplicidade confirmada (hash idêntico)."
        return s

    # 2) montar causas reais de AJUSTAR
    faltas = [k for k, v in checks.items() if not v]
    causas = []
    if dups.get("suspeita", False):
        causas.append("duplicidade suspeita")
    if REQUIRE_EMISSOR_VALIDO and em.get("valido") is None:
        causas.append("emissor indefinido")
    if faltas:
        # legenda amigável (opcional)
        legend = {
            "horas_ok": "horas abaixo do mínimo",
            "datas_ok": "data inválida",
            "aluno_ok": "nome do aluno não confere",
            "formato_ok": "título/tipo faltando"
        }
        causas += [legend.get(k, k) for k in faltas]

    if causas:
        s["status"] = "AJUSTAR"
        s["justificativa"] = "; ".join(causas)
        return s

    # 3) caso sem causas -> ACEITO
    s["status"] = "ACEITO"
    s["justificativa"] = "Regras atendidas e sem duplicidade."
    return s

def retornar_usuario(s: ValState) -> ValState:
    payload = {
        "certificadoId": s["dados"]["id"],
        "status": s["status"],
        "reason": s["justificativa"],
        "evidence": s.get("evidencias", []),
        "stateSnap": {k:s[k] for k in ["dados","checks","duplicidade","emissor","status","justificativa"] if k in s}
    }
    # grava auditoria e atualiza status no backend
    try: client.audit(payload)
    except Exception: pass
    try: client.set_status(s["dados"]["id"], s["status"])
    except Exception: pass
    return s

def _build():
    g = StateGraph(ValState)
    g.add_node("entrada_prisma", entrada_prisma)
    g.add_node("padronizar", padronizar)
    g.add_node("verificar_emissor", verificar_emissor)
    g.add_node("validar_regras_ies", validar_regras_ies)
    g.add_node("anti_duplicidade", anti_duplicidade)
    g.add_node("decidir_status", decidir_status)
    g.add_node("retornar_usuario", retornar_usuario)
    g.set_entry_point("entrada_prisma")
    g.add_edge("entrada_prisma","padronizar")
    g.add_edge("padronizar","verificar_emissor")
    g.add_edge("verificar_emissor","validar_regras_ies")
    g.add_edge("validar_regras_ies","anti_duplicidade")
    g.add_edge("anti_duplicidade","decidir_status")
    g.add_edge("decidir_status","retornar_usuario")
    g.add_edge("retornar_usuario", END)
    return g.compile()

_app = _build()

def run_validation(cert_id: str):
    result = _app.invoke({"cert_id": cert_id})
    return {
        "status": result.get("status"),
        "justificativa": result.get("justificativa"),
        "evidencias": result.get("evidencias", [])
    }
