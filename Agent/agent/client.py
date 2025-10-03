import httpx, os

API_BASE = os.getenv("BACKEND_BASE", "http://127.0.0.1:3000")
TIMEOUT = float(os.getenv("TIMEOUT_S", "5"))

def get_cert(cert_id: str):
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.get(f"{API_BASE}/certificados/{cert_id}")
        r.raise_for_status()
        return r.json()

def get_dup_fortes(file_hash: str, exclude_id: str | None = None):
    params = {"hash": file_hash}
    if exclude_id:
        params["excludeId"] = exclude_id
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.get(f"{API_BASE}/certificados/duplicatas", params=params)
        r.raise_for_status()
        return r.json()

def get_similares(qparams: dict):
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.get(f"{API_BASE}/certificados/similares", params=qparams)
        r.raise_for_status()
        return r.json()

def set_status(cert_id: str, status: str):
    path = {"ACEITO":"aceitar", "RECUSADO":"recusar", "AJUSTAR":"ajustar"}[status]
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.put(f"{API_BASE}/certificados/{cert_id}/{path}")
        r.raise_for_status()
        return r.json()

def audit(payload: dict):
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.post(f"{API_BASE}/auditoria", json=payload)
        r.raise_for_status()
        return r.json()

def get_issuer(name: str):
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.get(f"{API_BASE}/issuer", params={"name": name})
        if r.status_code == 200:
            return r.json()
        return None

def upsert_issuer(payload: dict):
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.post(f"{API_BASE}/issuer", json=payload)
        r.raise_for_status()
        return r.json()
