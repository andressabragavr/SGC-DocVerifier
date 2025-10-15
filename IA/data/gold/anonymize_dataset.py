# anonymize_dataset.py
from __future__ import annotations
import os, json, re, hashlib
from typing import Dict, Any
from unidecode import unidecode  # pip install Unidecode
from dotenv import load_dotenv

# --- Caminhos ---
DATA_DIR = os.path.abspath(os.path.dirname(__file__))

# arquivos dentro da MESMA pasta
SRC = os.path.join(DATA_DIR, "gold.jsonl")
DST = os.path.join(DATA_DIR, "gold_anon.jsonl")

# mapeamentos (na mesma pasta; coloque no .gitignore)
MAP_NAMES = os.path.join(DATA_DIR, ".mapping_names.json")
MAP_IDS   = os.path.join(DATA_DIR, ".mapping_ids.json")

# --- Config ---
load_dotenv()
# "pseudonym" = reversível com mapping; "hash" = irreversível
MODE = os.getenv("ANON_MODE", "pseudonym").lower()
# Sal para hashing (NÃO comitar no repo público)
SALT = os.getenv("ANON_SALT", "troque-este-sal-privado")

# --- Regex de PII ---
RE_EMAIL = re.compile(r"[\w\.\+\-]+@[\w\.-]+\.\w+", re.IGNORECASE)
RE_CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b")
RE_TEL = re.compile(r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b")

# --- Utilidades de mapping ---
def load_mapping_file(path: str) -> Dict[str, str]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_mapping_file(path: str, mp: Dict[str, str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mp, f, ensure_ascii=False, indent=2)

# --- Geração de pseudônimos/hashes ---
def gen_pseudonym(idx: int) -> str:
    return f"ALUNO_{idx:03d}"

def hash_name(name: str) -> str:
    h = hashlib.sha256((SALT + "|" + name).encode("utf-8")).hexdigest()[:8]
    return f"NOME_{h}"

def make_public_id(real_id: str) -> str:
    # determinístico e neutro: CERT_<hash8>
    h = hashlib.sha256((SALT + "|" + (real_id or "")).encode("utf-8")).hexdigest()[:8]
    return f"CERT_{h}"

# --- Redações/substituições ---
def replace_name_in_text(text: str, real: str, pseudo: str) -> str:
    """
    Substituição case/acentos-insensível do nome no texto OCR.
    Normaliza as duas strings sem acentos e compara por tokens.
    """
    if not real or not text:
        return text

    real_norm = unidecode(real).strip()
    if not real_norm:
        return text

    tokens = [re.escape(t) for t in real_norm.split()]
    if not tokens:
        return text

    # junta tokens permitindo múltiplos espaços/quebras
    pattern = r"".join([rf"{t}\s+" for t in tokens[:-1]] + [tokens[-1]])
    rx = re.compile(pattern, re.IGNORECASE)

    text_norm = unidecode(text)
    out = []
    i = 0
    for m in rx.finditer(text_norm):
        start, end = m.span()
        out.append(text[i:start])   # trecho original até o match
        out.append(pseudo)          # substitui pelo pseudônimo
        i = end
    out.append(text[i:])
    return "".join(out)

def redact_common_pii(text: str) -> str:
    text = RE_EMAIL.sub("<EMAIL>", text)
    text = RE_CPF.sub("<CPF>", text)
    text = RE_TEL.sub("<TELEFONE>", text)
    return text

# --- Núcleo de anonimização ---
def anonymize_record(
    rec: Dict[str, Any],
    mapping_names: Dict[str, str],
    mapping_ids: Dict[str, str],
    next_idx: int,
) -> tuple[Dict[str, Any], int]:
    rec = dict(rec)  # cópia rasa

    # 1) Nomes
    real_name_hint = (rec.get("hint_nome_aluno") or "").strip()
    real_name_gt   = (rec.get("gt_nome") or "").strip()
    base_name = real_name_gt or real_name_hint

    if MODE == "pseudonym":
        if base_name and base_name not in mapping_names:
            mapping_names[base_name] = gen_pseudonym(next_idx)
            next_idx += 1
        pseudo_name = mapping_names.get(base_name, gen_pseudonym(next_idx))
    else:
        pseudo_name = hash_name(base_name) if base_name else "ALUNO"

    ocr_text = rec.get("ocr_text") or ""
    ocr_text = replace_name_in_text(ocr_text, base_name, pseudo_name)
    ocr_text = redact_common_pii(ocr_text)

    rec["hint_nome_aluno"] = pseudo_name if real_name_hint else rec.get("hint_nome_aluno")
    rec["gt_nome"] = pseudo_name if real_name_gt else rec.get("gt_nome")
    rec["ocr_text"] = ocr_text

    for key in ("gt_titulo", "gt_instituicao"):
        if isinstance(rec.get(key), str):
            rec[key] = redact_common_pii(rec[key])

    # 2) ID
    real_id = rec.get("id") or ""
    if MODE == "pseudonym":
        if real_id and real_id not in mapping_ids:
            mapping_ids[real_id] = make_public_id(real_id)
        anon_id = mapping_ids.get(real_id, make_public_id(real_id))
    else:
        anon_id = make_public_id(real_id)

    # sobrescreve o id real pelo id anonimizado
    rec["id"] = anon_id

    return rec, next_idx

def run():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SRC):
        raise SystemExit(f"Arquivo não encontrado: {SRC}")

    mapping_names = load_mapping_file(MAP_NAMES) if MODE == "pseudonym" else {}
    mapping_ids   = load_mapping_file(MAP_IDS)   if MODE == "pseudonym" else {}
    next_idx = 1 + len(mapping_names)

    with open(SRC, "r", encoding="utf-8") as fin, open(DST, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            anon, next_idx = anonymize_record(rec, mapping_names, mapping_ids, next_idx)
            fout.write(json.dumps(anon, ensure_ascii=False) + "\n")

    if MODE == "pseudonym":
        save_mapping_file(MAP_NAMES, mapping_names)
        save_mapping_file(MAP_IDS, mapping_ids)

    print(f"OK: {DST}")

if __name__ == "__main__":
    run()
