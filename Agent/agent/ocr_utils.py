# agent/ocr_utils.py
import os, io, tempfile, shutil, mimetypes
from typing import Dict, Any, List, Tuple
import httpx
import pdfplumber
from pdf2image import convert_from_bytes
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import pytesseract

def _env_int(name: str, default: int) -> int:
    try:
        return int(float(os.getenv(name, str(default))))
    except Exception:
        return default

def _env_bool(name: str, default: bool = False) -> bool:
    v = str(os.getenv(name, "1" if default else "0")).strip().lower()
    return v in ("1", "true", "yes", "y", "on")

def _maybe_set_binaries():
    tpath = os.getenv("TESSERACT_CMD")
    if tpath:
        pytesseract.pytesseract.tesseract_cmd = tpath

def _download(url: str, timeout: float = 30.0) -> Tuple[bytes, str]:
    with httpx.Client(timeout=timeout) as c:
        r = c.get(url)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "")
        return r.content, content_type

def _preprocess(img: Image.Image) -> Image.Image:
    # Grayscale + leve aumento de contraste/nitidez + upscale 1.5x + binarização suave
    if img.mode != "L":
        img = ImageOps.grayscale(img)
    w, h = img.size
    img = img.resize((int(w * 1.5), int(h * 1.5)))
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img = img.filter(ImageFilter.SHARPEN)
    # Binarização simples (mantém legível para Tesseract sem OCR de baixa qualidade)
    img = img.point(lambda x: 255 if x > 200 else (0 if x < 110 else x))
    return img

def _ocr_images(images: List[Image.Image], langs: str) -> Tuple[str, List[Dict[str, Any]]]:
    pages_out: List[Dict[str, Any]] = []
    text_full = ""
    for i, img in enumerate(images):
        proc = _preprocess(img)
        txt = pytesseract.image_to_string(proc, lang=langs) or ""
        txt = txt.strip()
        pages_out.append({"page": i + 1, "text": txt})
        text_full += ("\n" + txt)
    return text_full.strip(), pages_out

def _pdf_to_images(pdf_bytes: bytes, dpi: int, page_limit: int) -> List[Image.Image]:
    poppler_path = os.getenv("POPPLER_PATH") or None
    images = convert_from_bytes(
        pdf_bytes,
        dpi=dpi,
        fmt="png",
        first_page=1,
        last_page=page_limit,
        poppler_path=poppler_path
    )
    # Garante que são PIL Images reais
    out = []
    for im in images:
        if not isinstance(im, Image.Image):
            im = Image.open(im)
        out.append(im)
    return out

def _try_native_text(pdf_bytes: bytes, page_limit: int) -> Tuple[str, List[Dict[str, Any]]]:
    pages_out: List[Dict[str, Any]] = []
    text_full = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, p in enumerate(pdf.pages):
            if i >= page_limit:
                break
            t = (p.extract_text() or "").strip()
            pages_out.append({"page": i + 1, "text": t})
            text_full += ("\n" + t)
    return text_full.strip(), pages_out

def _save_images_if_needed(images: List[Image.Image]) -> str | None:
    if not _env_bool("OCR_SAVE_IMAGES", False):
        return None
    tmpdir = tempfile.mkdtemp(prefix="ocr_imgs_")
    for i, im in enumerate(images):
        im.save(os.path.join(tmpdir, f"pagina_{i + 1}.png"), "PNG")
    return tmpdir

def extract_text_from_pdf_url(url: str) -> Dict[str, Any]:
    """
    Baixa o arquivo de `url`. Se for PDF:
      - OCR_MODE=force_ocr: converte para imagens e faz OCR
      - OCR_MODE=native_first (default): tenta texto nativo; se vazio, cai para OCR
    Se não for PDF (jpg/png/etc.), trata como imagem única e roda OCR.
    Retorna: {
        "text": str,
        "pages": [{"page": i, "text": str}],
        "mode": "native" | "ocr",
        "images_dir": str | None
    }
    """
    _maybe_set_binaries()

    dpi = _env_int("OCR_DPI", 250)
    page_limit = _env_int("OCR_PAGE_LIMIT", 6)
    langs = os.getenv("OCR_LANGS", "por+eng")
    mode = os.getenv("OCR_MODE", "native_first").strip().lower()

    file_bytes, content_type = _download(url)
    ext = (mimetypes.guess_extension(content_type) or "").lower()
    is_pdf = ("pdf" in content_type.lower()) or ext == ".pdf" or url.lower().endswith(".pdf")

    # Caso IMAGEM (não PDF): OCR direto na imagem única
    if not is_pdf:
        try:
            img = Image.open(io.BytesIO(file_bytes))
            text, pages = _ocr_images([img], langs)
            imgdir = _save_images_if_needed([img])
            return {"text": text, "pages": pages, "mode": "ocr", "images_dir": imgdir}
        except Exception:
            # fallback burro: salva em disco e tenta novamente
            with tempfile.NamedTemporaryFile(suffix=".bin", delete=True) as f:
                f.write(file_bytes); f.flush()
            return {"text": "", "pages": [], "mode": "ocr", "images_dir": None}

    # PDF
    if mode == "native_first":
        # 1) tenta nativo
        try:
            native_text, native_pages = _try_native_text(file_bytes, page_limit)
            if native_text.strip():
                return {"text": native_text, "pages": native_pages, "mode": "native", "images_dir": None}
        except Exception:
            pass
        # 2) cai para OCR (PDF->imagens)
        try:
            images = _pdf_to_images(file_bytes, dpi, page_limit)
            text, pages = _ocr_images(images, langs)
            imgdir = _save_images_if_needed(images)
            return {"text": text, "pages": pages, "mode": "ocr", "images_dir": imgdir}
        except Exception:
            return {"text": "", "pages": [], "mode": "ocr", "images_dir": None}

    else:  # force_ocr
        try:
            images = _pdf_to_images(file_bytes, dpi, page_limit)
            text, pages = _ocr_images(images, langs)
            imgdir = _save_images_if_needed(images)
            return {"text": text, "pages": pages, "mode": "ocr", "images_dir": imgdir}
        except Exception:
            # como fallback extremo, tenta nativo
            try:
                native_text, native_pages = _try_native_text(file_bytes, page_limit)
                if native_text.strip():
                    return {"text": native_text, "pages": native_pages, "mode": "native", "images_dir": None}
            except Exception:
                pass
            return {"text": "", "pages": [], "mode": "ocr", "images_dir": None}
