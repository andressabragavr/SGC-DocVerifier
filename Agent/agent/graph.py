from __future__ import annotations
from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime, timezone
from rapidfuzz import fuzz
from agent import client
import os
import re
from agent.ocr_utils import extract_text_from_pdf_url

# -------- envs / thresholds --------
H_MIN = int(float(os.getenv("H_MIN", "10")))
SIM_ALUNO = int(float(os.getenv("SIM_ALUNO", "92")))
SIM_DUP_FRACA = int(float(os.getenv("SIM_DUP_FRACA", "88")))

# thresholds para comparação OCR
THRESH_NOME_OCR = int(float(os.getenv("THRESH_NOME_OCR", "95")))
THRESH_INSTIT_OCR = int(float(os.getenv("THRESH_INSTIT_OCR", "90")))
THRESH_CURSO_OCR = int(float(os.getenv("THRESH_CURSO_OCR", "85")))
THRESH_NOME_FUZZY = int(float(os.getenv("THRESH_NOME_FUZZY", "80")))
THRESH_INSTIT_FUZZY = int(float(os.getenv("THRESH_INSTIT_FUZZY", "75")))
THRESH_CURSO_FUZZY = int(float(os.getenv("THRESH_CURSO_FUZZY", "70")))

# pesos duplicidade (mantidos)
W_INSTIT, W_NOME, W_DATA, W_HORAS = 40, 30, 20, 10

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
    campos_validacao: Dict[str, Any]
    ocr_text: str
    ocr_pages: List[Dict[str, Any]]

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

# ---------------------------------- nós ----------------------------------

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

# ------------ OCR local (pdfplumber -> fallback Tesseract) ------------
def carregar_ocr(s: ValState) -> ValState:
    url = (s.get("dados") or {}).get("urlPDF")
    if not url:
        s.setdefault("erros", []).append("sem_url_pdf")
        s.setdefault("evidencias", []).append({"tipo":"padronizacao","sub":"ocr_falhou","motivo":"sem_url"})
        s["ocr_text"] = ""
        s["ocr_pages"] = []
        return s
    try:
        ocr = extract_text_from_pdf_url(url)
        s["ocr_text"] = ocr.get("text","")
        s["ocr_pages"] = ocr.get("pages",[])
        s.setdefault("evidencias", []).append({"tipo":"padronizacao","sub":"ocr_carregado","modo":ocr.get("mode")})
    except Exception as e:
        s.setdefault("erros", []).append(f"ocr_erro:{e}")
        s["ocr_text"] = ""
        s["ocr_pages"] = []
        s.setdefault("evidencias", []).append({"tipo":"padronizacao","sub":"ocr_falhou"})
    return s

# ------------ Validação LLM (Prisma) × OCR por campo ------------
def _find_hours(txt: str) -> List[str]:
    return re.findall(r"\b(\d{1,3})\s*(h|horas)\b", txt, flags=re.IGNORECASE)

def _best_line_match(needle: str, hay: str) -> tuple[str,int]:
    lines = [ln.strip() for ln in (hay or "").splitlines() if ln.strip()]
    if not needle or not lines: return ("", 0)
    best = ""
    best_s = 0
    for ln in lines:
        sc = fuzz.token_set_ratio(needle, ln)
        if sc > best_s:
            best_s = sc
            best = ln
    return best, best_s

def validar_contra_ocr(s: ValState) -> ValState:
    d = s["dados"]
    ocr = s.get("ocr_text","") or ""
    evid = s.setdefault("evidencias", [])
    campos = {}

    # nome
    alvo_nome = d.get("nomeNoCertificado","")
    best, sc = _best_line_match(alvo_nome, ocr)
    status = "EXACT" if sc >= THRESH_NOME_OCR else ("FUZZY" if sc >= THRESH_NOME_FUZZY else "CONTRADICT")
    evid.append({"tipo":"ocr","campo":"nome","snippet":best[:180],"score":round(sc/100.0,3)})
    campos["nome"] = {"expected": alvo_nome, "status": status, "score": sc}

    # instituicao
    alvo_inst = d.get("instituicao","")
    best, sc = _best_line_match(alvo_inst, ocr)
    status = "EXACT" if sc >= THRESH_INSTIT_OCR else ("FUZZY" if sc >= THRESH_INSTIT_FUZZY else "CONTRADICT")
    evid.append({"tipo":"ocr","campo":"instituicao","snippet":best[:180],"score":round(sc/100.0,3)})
    campos["instituicao"] = {"expected": alvo_inst, "status": status, "score": sc}

    # data (dd/mm/aaaa ou "dd de mês de aaaa")
    alvo_data = d.get("dataConclusao")
    datas = re.findall(r"\b(\d{1,2}/\d{1,2}/\d{2,4}|[0-3]?\d\s+de\s+[A-Za-zçãé]+\s+de\s+\d{4})\b", ocr)
    if alvo_data and datas:
        evid.append({"tipo":"ocr","campo":"data","snippet":str(datas[:3])[:180],"score":1.0})
        campos["data"] = {"expected": alvo_data, "status": "EXACT", "score": 100}
    else:
        evid.append({"tipo":"ocr","campo":"data","snippet":"-", "score":0.0})
        campos["data"] = {"expected": alvo_data, "status": "MISSING", "score": 0}

    # horas (número + h/horas)
    alvo_horas = str(d.get("horasAtribuidas") or "")
    hs = _find_hours(ocr)
    if alvo_horas and hs:
        nums = {h[0] for h in hs}
        ok = alvo_horas in nums
        evid.append({"tipo":"ocr","campo":"horas","snippet":str(list(nums)[:4]),"score":1.0 if ok else 0.6})
        campos["horas"] = {"expected": alvo_horas, "status": "EXACT" if ok else "FUZZY", "score": 100 if ok else 60}
    else:
        evid.append({"tipo":"ocr","campo":"horas","snippet":"-", "score":0.0})
        campos["horas"] = {"expected": alvo_horas, "status": "MISSING", "score": 0}

    # curso/titulo
    alvo_tit = d.get("titulo","")
    best, sc = _best_line_match(alvo_tit, ocr)
    status = "EXACT" if sc >= THRESH_CURSO_OCR else ("FUZZY" if sc >= THRESH_CURSO_FUZZY else "CONTRADICT")
    evid.append({"tipo":"ocr","campo":"curso","snippet":best[:180],"score":round(sc/100.0,3)})
    campos["curso"] = {"expected": alvo_tit, "status": status, "score": sc}

    s["campos_validacao"] = campos
    return s

# ------------ Regras IES existentes (mantidas) ------------
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

# ------------ Anti-duplicidade (mantido) ------------
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

# ------------ Decisão BINÁRIA (ACEITO | RECUSADO) ------------
def decidir_status(s: ValState) -> ValState:
    d = s["dados"]
    dups = s.get("duplicidade", {})
    campos = s.get("campos_validacao", {})
    checks = s.get("checks", {})

    motivos = []

    # 1) duplicidade forte reprova
    if dups.get("confirmada"):
        s["status"] = "RECUSADO"
        s["justificativa"] = "Duplicidade confirmada (hash idêntico)."
        return s

    # 2) regras de negócio
    hoje = datetime.utcnow().date().isoformat()
    if d["horasAtribuidas"] < H_MIN:
        motivos.append(f"horas abaixo do mínimo ({d['horasAtribuidas']}<{H_MIN})")
    if not d["dataConclusao"] or d["dataConclusao"] > hoje:
        motivos.append("data inválida ou futura")

    # 3) similaridade do aluno (já computada)
    if "aluno_ok" in checks and not checks["aluno_ok"]:
        motivos.append("nome do aluno não confere com o usuário")

    # 4) campos críticos a partir do OCR
    criticos = ["nome","instituicao","data","horas","curso"]
    for k in criticos:
        st = (campos.get(k) or {}).get("status")
        if st in ("MISSING","CONTRADICT"):
            motivos.append(f"campo {k} não confirmado ({st})")

    if motivos:
        s["status"] = "RECUSADO"
        s["justificativa"] = "; ".join(motivos)
        return s

    s["status"] = "ACEITO"
    s["justificativa"] = "Campos confirmados no OCR e sem duplicidade."
    return s

# ------------ Auditoria/retorno (mantido) ------------
def retornar_usuario(s: ValState) -> ValState:
    payload = {
        "certificadoId": s["dados"]["id"],
        "status": s["status"],
        "reason": s["justificativa"],
        "evidence": s.get("evidencias", []),
        "stateSnap": {k:s[k] for k in ["dados","checks","duplicidade","emissor","status","justificativa","campos_validacao"] if k in s}
    }
    try: client.audit(payload)
    except Exception: pass
    try: client.set_status(s["dados"]["id"], s["status"])
    except Exception: pass
    return s

# ------------ (opcional) verificador de emissor – deixado aqui para futuro uso ------------
REQUIRE_EMISSOR_VALIDO = False
EMISSOR_CACHE_CONF_MIN = float(os.getenv("EMISSOR_CACHE_CONF_MIN", "0.7"))
def verificar_emissor(s: ValState) -> ValState:
    # Mantido para uso futuro (web); não está ligado no grafo por ora.
    return s

# ------------ Build do grafo (nova ordem) ------------
def _build():
    g = StateGraph(ValState)
    g.add_node("entrada_prisma", entrada_prisma)
    g.add_node("padronizar", padronizar)
    g.add_node("carregar_ocr", carregar_ocr)
    g.add_node("validar_contra_ocr", validar_contra_ocr)
    g.add_node("validar_regras_ies", validar_regras_ies)
    g.add_node("anti_duplicidade", anti_duplicidade)
    g.add_node("decidir_status", decidir_status)
    g.add_node("retornar_usuario", retornar_usuario)

    g.set_entry_point("entrada_prisma")
    g.add_edge("entrada_prisma","padronizar")
    g.add_edge("padronizar","carregar_ocr")
    g.add_edge("carregar_ocr","validar_contra_ocr")
    g.add_edge("validar_contra_ocr","validar_regras_ies")
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
