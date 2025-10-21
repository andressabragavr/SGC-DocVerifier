# application/services/dataset_logger.py
from __future__ import annotations
from typing import Dict, Any, Optional
import os, json, datetime

IA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET_PATH = os.path.join(IA_ROOT, "data", "gold", "gold.jsonl")

def _ensure_dirs(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

def _now_iso() -> str:
    # mantém timestamp útil para auditoria interna (não é campo obrigatório no dataset final)
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def _to_int_or_none(x) -> Optional[int]:
    try:
        return int(str(x).strip())
    except Exception:
        return None

def build_record(
    *,
    cert_id: str,
    hint_nome_aluno: str,
    curso_aluno: str,
    inscricao_aluno_ano: str,
    ocr_text: str,
    llm_json: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Constrói 1 linha no esquema mínimo acordado (somente campos obrigatórios).
    llm_json é a lista com 1 objeto retornado pela LLM (seu caso atual).
    """
    item = llm_json[0] if isinstance(llm_json, list) and llm_json else {}

    # normalizações leves (sem alterar seu core):
    semestre = item.get("semestre")
    if isinstance(semestre, str) and "-" in semestre and semestre.count("-") == 1:
        # aceita "2023-2" -> "2023-S2"
        ano, sem = semestre.split("-")
        if sem.strip() in {"1", "2"}:
            semestre = f"{ano}-S{sem.strip()}"

    horas = _to_int_or_none(item.get("quantidade_horas"))

    return {
        "id": cert_id,
        "hint_nome_aluno": hint_nome_aluno,
        "get_curso": curso_aluno,
        "get_ano_inscricao": inscricao_aluno_ano,
        "ocr_text": ocr_text,
        "gt_semestre": semestre if semestre else None,
        "gt_instituicao": item.get("instituicao") or None,
        "gt_tipo_certificado": item.get("tipo_certificado") or None,
        "gt_titulo": item.get("titulo") or None,
        "gt_quantidade_horas": horas,
        "gt_data_conclusao": item.get("data_conclusao") or None,
        "gt_nome": item.get("nome") or None,
        "gt_relacao_com_curso": item.get("relacao_com_curso") or "Não",
        # interno: útil pra rastrear, não é obrigatório — pode remover se quiser
        "_logged_at": _now_iso(),
    }

def append_jsonl(record: Dict[str, Any], dataset_path: str = DATASET_PATH) -> None:
    _ensure_dirs(dataset_path)
    # append atômico simples
    line = json.dumps(record, ensure_ascii=False)
    with open(dataset_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")