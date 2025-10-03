# agent/ocr_utils.py
import os, io, tempfile
import httpx
from typing import Dict, Any, List
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

def _env_int(name: str, default: int) -> int:
    try: return int(float(os.getenv(name, str(default))))
    except Exception: return default

def extract_text_from_pdf_url(url: str) -> Dict[str, Any]:
    """
    Baixa o PDF de `url`, tenta extrair texto nativo; se vier vazio, faz OCR com Tesseract.
    Retorna: {"text": "...", "pages": [{"page": i, "text": "..."}], "mode": "native"|"ocr"}
    """
    dpi = _env_int("OCR_DPI", 200)
    page_limit = _env_int("OCR_PAGE_LIMIT", 6)
    langs = os.getenv("OCR_LANGS", "por+eng")

    # 1) baixar PDF
    with httpx.Client(timeout=30.0) as c:
        r = c.get(url)
        r.raise_for_status()
        pdf_bytes = r.content

    pages_out: List[Dict[str, Any]] = []
    text_full = ""

    # 2) tentar texto nativo (pdfplumber)
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for i, p in enumerate(pdf.pages):
                if i >= page_limit: break
                t = (p.extract_text() or "").strip()
                pages_out.append({"page": i+1, "text": t})
                text_full += ("\n" + t)
        if text_full.strip():
            return {"text": text_full.strip(), "pages": pages_out, "mode": "native"}
    except Exception:
        pass

    # 3) fallback: OCR com tesseract (pdf2image -> PIL -> pytesseract)
    # usa arquivo temporário pois convert_from_path precisa de path
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as f:
        f.write(pdf_bytes)
        f.flush()
        images = convert_from_path(f.name, dpi=dpi, fmt="png", first_page=1, last_page=page_limit)

    pages_out = []
    text_full = ""
    for i, img in enumerate(images):
        if not isinstance(img, Image.Image):
            img = Image.open(img)
        t = pytesseract.image_to_string(img, lang=langs) or ""
        t = t.strip()
        pages_out.append({"page": i+1, "text": t})
        text_full += ("\n" + t)

    return {"text": text_full.strip(), "pages": pages_out, "mode": "ocr"}
