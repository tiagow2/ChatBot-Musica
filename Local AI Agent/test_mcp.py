"""
Teste simples para o servidor MCP (FastAPI).
Executa: CREATE -> LIST -> SEARCH -> UPDATE -> DELETE

Execute com:
    python "Local AI Agent/test_mcp.py"

Requer: requests (já listado em requirements.txt)
"""
import requests
import json

BASE = "http://127.0.0.1:8000"

def pretty(r):
    try:
        return json.dumps(r.json(), indent=2, ensure_ascii=False)
    except Exception:
        return str(r.text)

if __name__ == '__main__':
    print('=== MCP TEST START ===')

    # 1) CREATE
    payload = {
        "id": "song-1",
        "title": "Minha Música",
        "text": "Trecho da letra original",
        "source": "test_script"
    }
    r = requests.post(f"{BASE}/add", json=payload)
    print('\nCREATE (/add) ->', r.status_code)
    print(pretty(r))

    # 2) LIST
    r = requests.get(f"{BASE}/list")
    print('\nLIST (/list) ->', r.status_code)
    print(pretty(r))

    # 3) SEARCH
    payload = {"query": "Trecho da letra", "k": 3}
    r = requests.post(f"{BASE}/search", json=payload)
    print('\nSEARCH (/search) ->', r.status_code)
    print(pretty(r))

    # 4) UPDATE (re-add same id with modified text)
    payload = {
        "id": "song-1",
        "title": "Minha Música (v2)",
        "text": "Trecho da letra atualizado",
        "source": "test_script"
    }
    r = requests.post(f"{BASE}/add", json=payload)
    print('\nUPDATE (/add same id) ->', r.status_code)
    print(pretty(r))

    # 5) DELETE
    payload = {"id": "song-1"}
    r = requests.post(f"{BASE}/delete", json=payload)
    print('\nDELETE (/delete) ->', r.status_code)
    print(pretty(r))

    print('\n=== MCP TEST END ===')
