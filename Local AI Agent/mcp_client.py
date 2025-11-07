import requests
from typing import Optional, List, Dict, Any

BASE = "http://127.0.0.1:8000"


def is_alive(timeout: float = 1.0) -> bool:
    try:
        r = requests.get(f"{BASE}/list", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def add_doc(doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> bool:
    payload = {"id": doc_id, "text": text, "metadata": metadata or {}}
    try:
        r = requests.post(f"{BASE}/add", json=payload, timeout=timeout)
        return r.ok
    except Exception:
        return False


def search(query: str, k: int = 3, timeout: float = 5.0) -> List[Dict[str, Any]]:
    payload = {"query": query, "k": k}
    try:
        r = requests.post(f"{BASE}/search", json=payload, timeout=timeout)
        if r.ok:
            return r.json().get("results", [])
    except Exception:
        pass
    return []
