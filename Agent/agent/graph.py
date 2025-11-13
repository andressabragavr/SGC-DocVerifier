from __future__ import annotations
from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime, timezone
from rapidfuzz import fuzz
from agent import client
import os
import re
from agent.ocr_utils import extract_text_from_pdf_url
from agent.atividades_data import MAP_HORAS
import logging
from agent.issuer_agent import issuer_verify

REQUIRE_EMISSOR_VALIDO = True
EMISSOR_CONF_MIN = float(os.getenv("EMISSOR_CONF_MIN", "0.85"))

# logo no topo do arquivo (graph.py), configure um logging simples:
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# -------- envs / thresholds --------
H_MIN = int(float(os.getenv("H_MIN", "1")))
SIM_ALUNO = int(float(os.getenv("SIM_ALUNO", "92")))
SIM_DUP_FRACA = int(float(os.getenv("SIM_DUP_FRACA", "88")))

# thresholds para comparação OCR
THRESH_NOME_OCR = int(float(os.getenv("THRESH_NOME_OCR", "95")))
THRESH_INSTIT_OCR = int(float(os.getenv("THRESH_INSTIT_OCR", "90")))
THRESH_CURSO_OCR = int(float(os.getenv("THRESH_CURSO_OCR", "85")))
THRESH_NOME_FUZZY = int(float(os.getenv("THRESH_NOME_FUZZY", "70")))
THRESH_INSTIT_FUZZY = int(float(os.getenv("THRESH_INSTIT_FUZZY", "75")))
THRESH_CURSO_FUZZY = int(float(os.getenv("THRESH_CURSO_FUZZY", "70")))

# pesos duplicidade (mantidos)
W_INSTIT, W_NOME, W_DATA, W_HORAS = 40, 30, 20, 10
ALLOW_INFER_HOURS = int(os.getenv("ALLOW_INFER_HOURS", "1")) == 1
INFER_STRICT_MATCH = int(os.getenv("INFER_STRICT_MATCH", "1")) == 1

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
    if not d:
        return None
    try:
        s = str(d)
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc).date().isoformat()
    except Exception:
        return None

def _sim_nome(a: str, b: str) -> int:
    return fuzz.token_set_ratio(_norm(a).lower(), _norm(b).lower())

def _score_dup(ref: Dict[str, Any], cand: Dict[str, Any]) -> int:
    s_inst = fuzz.token_set_ratio(
        _norm(ref.get("instituicao")), _norm(cand.get("instituicao")))
    s_nome = _sim_nome(ref.get("nomeNoCertificado", ""),
                       cand.get("nomeNoCertificado", ""))
    s_data = 100 if _iso_date(ref.get("dataConclusao")) == _iso_date(
        cand.get("dataConclusao")) else 0
    s_hora = 100 if int(ref.get("horasAtribuidas") or 0) == int(
        cand.get("horasAtribuidas") or 0) else 0
    total = (s_inst*W_INSTIT + s_nome*W_NOME + s_data*W_DATA +
             s_hora*W_HORAS) / (W_INSTIT+W_NOME+W_DATA+W_HORAS)
    return int(round(total))

# ---------------------------------- nós ----------------------------------
def entrada_prisma(s: ValState) -> ValState:
    s["dados_raw"] = client.get_cert(s["cert_id"])
    return s

def padronizar(s: ValState) -> ValState:
    c = s["dados_raw"]
    s["dados"] = {
        "id": c.get("id"),
        "userName": c.get("user", {}).get("name", ""),
        "userRa": c.get("user", {}).get("ra", ""),
        "instituicao": _norm(c.get("instituicao")),
        "nomeNoCertificado": _norm(c.get("nomeNoCertificado")),
        "dataConclusao": _iso_date(c.get("dataConclusao")),
        "horasAtribuidas": int(c.get("horasAtribuidas") or 0),
        "fileHashSHA256": c.get("fileHashSHA256"),
        "titulo": _norm(c.get("titulo")),
        "tipoAtividade": _norm(c.get("tipoAtividade")),
        "urlPDF": c.get("urlPDF")
    }
    s.setdefault("evidencias", []).append({"tipo": "padronizacao"})
    return s

# ------------ OCR local (pdfplumber -> fallback Tesseract) ------------
def _preview(text: str, n: int = 800) -> str:
    text = (text or "").replace("\r", " ").strip()
    return (text[:n] + ("…[cut]" if len(text) > n else ""))

def carregar_ocr(s: ValState) -> ValState:
    url = (s.get("dados") or {}).get("urlPDF")
    if not url:
        s.setdefault("erros", []).append("sem_url_pdf")
        s.setdefault("evidencias", []).append(
            {"tipo": "padronizacao", "sub": "ocr_falhou", "motivo": "sem_url"})
        s["ocr_text"] = ""
        s["ocr_pages"] = []
        return s
    try:
        ocr = extract_text_from_pdf_url(url)
        s["ocr_text"] = ocr.get("text", "")
        s["ocr_pages"] = ocr.get("pages", [])
        ev = {"tipo": "padronizacao", "sub": "ocr_carregado", "modo": ocr.get("mode")}
        if ocr.get("images_dir"):
            ev["images_dir"] = ocr["images_dir"]
        s.setdefault("evidencias", []).append(ev)

        # >>> PREVIEW NO LOG <<<
        if os.getenv("OCR_DEBUG", "0") == "1":
            n = int(os.getenv("OCR_PREVIEW_CHARS", "800"))
            logging.info(
                "[OCR PREVIEW] cert_id=%s mode=%s\n%s",
                s.get("cert_id"),
                ocr.get("mode"),
                _preview(s["ocr_text"], n),
            )
            # se quiser ver página a página:
            for p in s.get("ocr_pages", [])[:3]:  # limita a 3 páginas no log
                logging.info("[OCR PAGE %s] %s", p.get("page"), _preview(p.get("text",""), 400))

    except Exception as e:
        s.setdefault("erros", []).append(f"ocr_erro:{e}")
        s["ocr_text"] = ""
        s["ocr_pages"] = []
        s.setdefault("evidencias", []).append({"tipo": "padronizacao", "sub": "ocr_falhou"})
    return s

# ------------ Validação LLM (Prisma) × OCR por campo ------------
def _find_hours(txt: str) -> List[str]:
    """Captura 40h, 40 h, 40h/a, 40 horas(-aula), CH: 40, 'carga horária: 40' etc."""
    nums = set()  # 1) 40h / 40 h / 40h/a / 40 horas / 40 horas-aula
    for m in re.finditer(r"\b(\d{1,3})\s*(?:h(?:\/a|\.?a\.?|oras(?:-aula)?)?)\b", txt, flags=re.IGNORECASE):
        nums.add(m.group(1))

    # 2) carga horária: 40
    for m in re.finditer(r"carga\s*hor[áa]ria[^0-9]{0,20}(\d{1,3})", txt, flags=re.IGNORECASE):
        nums.add(m.group(1))

    # 3) CH: 40
    for m in re.finditer(r"\bCH[:\s\-]*([0-9]{1,3})\b", txt, flags=re.IGNORECASE):
        nums.add(m.group(1))

    # 4) 40 , horas
    for m in re.finditer(r"\b(\d{1,3})\b\s*[,;:·.-]?\s*horas(?:-aula)?\b", txt, flags=re.IGNORECASE):
        nums.add(m.group(1))

    return list(nums)

def _best_line_match(needle: str, hay: str) -> tuple[str, int]:
    # remove pontuação pesada e compara por várias métricas
    hay = re.sub(r"[^\w\sÀ-ÿ]", " ", hay or "")
    lines = [ln.strip() for ln in hay.splitlines() if ln.strip()]
    if not needle or not lines:
        return ("", 0)
    best = ""
    best_s = 0
    for ln in lines:
        s1 = fuzz.token_set_ratio(needle, ln)
        s2 = fuzz.partial_ratio(needle, ln)
        s3 = fuzz.WRatio(needle, ln)
        sc = max(s1, s2, s3)

        if sc > best_s:
            best_s, best = sc, ln
    return best, best_s

def validar_contra_ocr(s: ValState) -> ValState:
    d = s["dados"]
    ocr = s.get("ocr_text", "") or ""
    evid = s.setdefault("evidencias", [])
    campos = {}

    # -------- nome (tenta nome do certificado; se fraco, tenta userName) --------
    alvo_nome = d.get("nomeNoCertificado", "") or ""
    best, sc = _best_line_match(alvo_nome, ocr)

    if sc < THRESH_NOME_FUZZY:
        alt = d.get("userName", "") or ""
        if alt and alt != alvo_nome:
            best2, sc2 = _best_line_match(alt, ocr)
            if sc2 > sc:
                alvo_nome, best, sc = alt, best2, sc2

    status = "EXACT" if sc >= THRESH_NOME_OCR else (
        "FUZZY" if sc >= THRESH_NOME_FUZZY else "CONTRADICT")
    evid.append({"tipo": "ocr", "campo": "nome",
                "snippet": best[:180], "score": round(sc/100.0, 3)})
    campos["nome"] = {"expected": alvo_nome, "status": status, "score": sc}

    # -------- instituição --------
    alvo_inst = d.get("instituicao", "")
    best, sc = _best_line_match(alvo_inst, ocr)
    status = "EXACT" if sc >= THRESH_INSTIT_OCR else (
        "FUZZY" if sc >= THRESH_INSTIT_FUZZY else "CONTRADICT")
    evid.append({"tipo": "ocr", "campo": "instituicao",
                "snippet": best[:180], "score": round(sc/100.0, 3)})
    campos["instituicao"] = {
        "expected": alvo_inst, "status": status, "score": sc}

    # -------- data (compara presença; se quiser, depois normalizamos) --------
    alvo_data = d.get("dataConclusao")
    datas = re.findall(
        r"\b(\d{1,2}/\d{1,2}/\d{2,4}|[0-3]?\d\s+de\s+[A-Za-zçãé]+\s+de\s+\d{4})\b", ocr)
    if alvo_data and datas:
        evid.append({"tipo": "ocr", "campo": "data",
                    "snippet": str(datas[:3])[:180], "score": 1.0})
        campos["data"] = {"expected": alvo_data,
                          "status": "EXACT", "score": 100}
    else:
        evid.append({"tipo": "ocr", "campo": "data",
                    "snippet": "-", "score": 0.0})
        campos["data"] = {"expected": alvo_data,
                          "status": "MISSING", "score": 0}

    # -------- horas (OCR) + fallback por tipo (INFERRED) --------
    alvo_horas = str(d.get("horasAtribuidas") or "")
    hs = _find_hours(ocr)
    if alvo_horas and hs:
        nums = {h for h in hs}  # _find_hours já retorna só números
        ok = alvo_horas in nums
        evid.append({"tipo": "ocr", "campo": "horas", "snippet": str(
            list(nums)[:4]), "score": 1.0 if ok else 0.6})
        campos["horas"] = {
            "expected": alvo_horas, "status": "EXACT" if ok else "FUZZY", "score": 100 if ok else 60}
    else:
        if ALLOW_INFER_HOURS:
            tipo = d.get("tipoAtividade") or ""
            infer = MAP_HORAS.get(tipo)
            if infer is not None:
                coerente = True
                if INFER_STRICT_MATCH:
                    coerente = (
                        str(infer) == alvo_horas) if alvo_horas else True
                evid.append({"tipo": "ocr", "campo": "horas",
                            "snippet": f"INFERIDO:{infer}", "score": 1.0 if coerente else 0.5})
                evid.append({"tipo": "regra", "campo": "horas_inferidas",
                            "fonte": "atividades_data", "tipoAtividade": tipo, "valor": infer})
                campos["horas"] = {"expected": str(
                    alvo_horas or infer), "status": "INFERRED" if coerente else "FUZZY", "score": 100 if coerente else 50}
            else:
                evid.append({"tipo": "ocr", "campo": "horas",
                            "snippet": "-", "score": 0.0})
                campos["horas"] = {"expected": alvo_horas,
                                   "status": "MISSING", "score": 0}
        else:
            evid.append({"tipo": "ocr", "campo": "horas",
                        "snippet": "-", "score": 0.0})
            campos["horas"] = {"expected": alvo_horas,
                               "status": "MISSING", "score": 0}

    # -------- curso/título --------
    alvo_tit = d.get("titulo", "")
    best, sc = _best_line_match(alvo_tit, ocr)
    status = "EXACT" if sc >= THRESH_CURSO_OCR else (
        "FUZZY" if sc >= THRESH_CURSO_FUZZY else "CONTRADICT")
    evid.append({"tipo": "ocr", "campo": "curso",
                "snippet": best[:180], "score": round(sc/100.0, 3)})
    campos["curso"] = {"expected": alvo_tit, "status": status, "score": sc}

    s["campos_validacao"] = campos
    return s

# ------------ Regras IES existentes (mantidas) ------------
def validar_regras_ies(s: ValState) -> ValState:
    d = s["dados"]
    hoje = datetime.utcnow().date().isoformat()
    horas_ok = d["horasAtribuidas"] >= H_MIN
    datas_ok = (d["dataConclusao"] is not None) and (
        d["dataConclusao"] <= hoje)
    aluno_ok = _sim_nome(d.get("nomeNoCertificado", ""),
                         d.get("userName", "")) >= SIM_ALUNO
    formato_ok = bool(d.get("titulo")) and bool(d.get("tipoAtividade"))
    s["checks"] = dict(horas_ok=horas_ok, datas_ok=datas_ok,
                       aluno_ok=aluno_ok, formato_ok=formato_ok)
    ev = s.setdefault("evidencias", [])
    ev += [
        {"tipo": "regra", "campo": "horas", "ok": horas_ok,
            "valor": d["horasAtribuidas"], "minimo": H_MIN},
        {"tipo": "regra", "campo": "dataConclusao", "ok": datas_ok,
            "valor": d["dataConclusao"], "ate": hoje},
        {"tipo": "regra", "campo": "aluno", "ok": aluno_ok}, {
            "tipo": "regra", "campo": "formato", "ok": formato_ok},
    ]
    return s

# ------------ Anti-duplicidade (mantido) ------------
def anti_duplicidade(s: ValState) -> ValState:
    d = s["dados"]
    fortes = client.get_dup_fortes(
        d.get("fileHashSHA256"), exclude_id=d.get("id"))
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
        ev.append({"tipo": "duplicidade", "modo": "similaridade",
                   "top": s["duplicidade"]["matches"][:3]})
    else:
        ev.append({"tipo": "duplicidade", "modo": "analise",
                   "resultado": "sem_suspeita"})
    return s

# ------------ Decisão BINÁRIA (ACEITO | RECUSADO) ------------
def decidir_status(s: ValState) -> ValState:
    d = s["dados"]
    dups = s.get("duplicidade", {})
    campos = s.get("campos_validacao", {})
    checks = s.get("checks", {})
    emissor = s.get("emissor", {}) or {}

    motivos = []

    # 1) duplicidade forte reprova
    if dups.get("confirmada"):
        s["status"] = "RECUSADO"
        s["justificativa"] = "Duplicidade confirmada (hash idêntico)."
        return s

    # 2) regras de negócio
    hoje = datetime.utcnow().date().isoformat()
    if d["horasAtribuidas"] < H_MIN:
        motivos.append(
            f"horas abaixo do mínimo ({d['horasAtribuidas']}<{H_MIN})")
    if not d["dataConclusao"] or d["dataConclusao"] > hoje:
        motivos.append("data inválida ou futura")

    # 3) similaridade do aluno (já computada)
    if "aluno_ok" in checks and not checks["aluno_ok"]:
        motivos.append("nome do aluno não confere com o usuário")

    # 4) campos críticos a partir do OCR
    criticos = ["nome", "instituicao", "data", "horas", "curso"]
    for k in criticos:
        st = (campos.get(k) or {}).get("status")
        if st in ("MISSING", "CONTRADICT"):
            motivos.append(f"campo {k} não confirmado ({st})")
            
    # 5) emissor (se exigir e não for válido)
    if REQUIRE_EMISSOR_VALIDO:
        conf = float(emissor.get("confianca", 0.0) or 0.0)
        valido = emissor.get("valido")
        if not (valido is True and conf >= EMISSOR_CONF_MIN):
            motivos.append("emissor não verificado na web (ou confiança insuficiente)")

    if motivos:
        s["status"] = "RECUSADO"
        s["justificativa"] = "; ".join(motivos)
        return s

    s["status"] = "ACEITO"
    s["justificativa"] = "Campos confirmados no OCR, emissor verificado na web e sem duplicidade."

    return s

# ------------ Auditoria/retorno (mantido) ------------
def retornar_usuario(s: ValState) -> ValState:
    payload = {
        "certificadoId": s["dados"]["id"],
        "status": s["status"],
        "reason": s["justificativa"],
        "evidence": s.get("evidencias", []),
        "stateSnap": {k: s[k] for k in
                      ["dados", "checks", "duplicidade", "emissor", "status", "justificativa", "campos_validacao"] if k in s}
    }
    try:
        client.audit(payload)
    except Exception:
        pass
    try:
        client.set_status(s["dados"]["id"], s["status"])
    except Exception:
        pass
    return s

# ------------ (opcional) verificador de emissor – deixado aqui para futuro uso ------------
EMISSOR_CACHE_CONF_MIN = float(os.getenv("EMISSOR_CACHE_CONF_MIN", "0.7"))

def verificar_emissor(s: ValState) -> ValState:
    d = s.get("dados", {})
    campos = s.get("campos_validacao", {}) or {}
    nome_backend = (d.get("instituicao") or "").strip()
    nome_ocr_snippet = ((campos.get("instituicao") or {}).get("snippet") or "").strip()

    # candidatos deduplicados e não vazios
    candidatos = [x for x in {nome_backend, nome_ocr_snippet} if x]

    if not candidatos:
        s.setdefault("evidencias", []).append({"tipo": "emissor", "resultado": "sem_nome"})
        s["emissor"] = {"valido": None, "confianca": 0.0, "evidencias": []}
        return s

    # tenta cache apenas pelo nome do backend
    cached = None
    try:
        if nome_backend:
            cached = client.get_issuer(nome_backend)
    except Exception:
        cached = None

    if cached and float(cached.get("confianca", 0) or 0) >= EMISSOR_CACHE_CONF_MIN:
        s["emissor"] = cached
        s.setdefault("evidencias", []).append({
            "tipo": "emissor", "fonte": cached.get("fonte","cache"),
            "confianca": cached.get("confianca"), "evidencias": cached.get("evidencias", [])
        })
        return s

    # consulta web: tenta o melhor resultado entre os candidatos
    year_hint = None
    try:
        if d.get("dataConclusao"):
            year_hint = str(datetime.fromisoformat(d["dataConclusao"]).year)
    except Exception:
        pass
    melhores = []
    for cand in candidatos:
        res = issuer_verify(cand, year_hint=year_hint)
        melhores.append((res.get("confianca") or 0.0, cand, res))
    melhores.sort(reverse=True, key=lambda x: x[0])
    conf, usado, res = (melhores[0] if melhores else (0.0, nome_backend, {"valido": None, "confianca": 0.0, "evidencias": [], "fonte":"duck-free"}))

    s["emissor"] = res
    s.setdefault("evidencias", []).append({
        "tipo": "emissor",
        "consulta_usada": usado,
        "fonte": res.get("fonte"),
        "confianca": res.get("confianca"),
        "evidencias": res.get("evidencias", [])
    })

    # grava no backend (use o nome do backend se existir; senão o usado)
    try:
        client.upsert_issuer({
            "nome": nome_backend or usado,
            "valido": res.get("valido"),
            "confianca": res.get("confianca"),
            "evidencias": res.get("evidencias", []),
            "fonte": res.get("fonte", "")
        })
    except Exception as e:
        logging.info("issuer upsert falhou: %s", e)

    return s

# ------------ Build do grafo (nova ordem) ------------
def _build():
    g = StateGraph(ValState)
    g.add_node("entrada_prisma", entrada_prisma)
    g.add_node("padronizar", padronizar)
    g.add_node("carregar_ocr", carregar_ocr)
    g.add_node("validar_contra_ocr", validar_contra_ocr)
    g.add_node("validar_regras_ies", validar_regras_ies)
    g.add_node("verificar_emissor", verificar_emissor)
    g.add_node("anti_duplicidade", anti_duplicidade)
    g.add_node("decidir_status", decidir_status)
    g.add_node("retornar_usuario", retornar_usuario)

    g.set_entry_point("entrada_prisma")

    g.add_edge("entrada_prisma", "padronizar")
    g.add_edge("padronizar", "carregar_ocr")
    g.add_edge("carregar_ocr", "validar_contra_ocr")
    g.add_edge("validar_contra_ocr", "validar_regras_ies")
    g.add_edge("validar_regras_ies", "verificar_emissor")
    g.add_edge("verificar_emissor", "anti_duplicidade")
    g.add_edge("anti_duplicidade", "decidir_status")
    g.add_edge("decidir_status", "retornar_usuario")
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