"""SQLite-based MCP server (leve) — API REST para adicionar e buscar documentos.

Este servidor armazena textos e embeddings em uma base SQLite. Para pequenas
quantidades de dados faz buscas por similaridade carregando embeddings e
calculando similaridade em memória (cosine). Não usa FAISS, assim evita
problemas de instalação em Windows.

Endpoints:
 - POST /add: {"id":"id", "text":"...", "metadata":{...}} -> adiciona/atualiza doc
 - POST /search: {"query":"texto", "k":3} -> retorna os k melhores documentos
 - GET  /list -> lista ids
 - POST /delete: {"id":"..."} -> remove

Execute: python mcp_server.py  (vai subir o uvicorn se disponível)
"""

import json
import sqlite3
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

import numpy as np

DB_PATH = "./local_agent_data/mcp.sqlite"


class AddRequest(BaseModel):
    id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str
    k: int = 3


class DeleteRequest(BaseModel):
    id: str


app = FastAPI(title="SQLite MCP Server")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def ensure_table(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS docs (
            id TEXT PRIMARY KEY,
            text TEXT,
            metadata TEXT,
            embedding TEXT
        )
        """
    )
    conn.commit()


def embed_text(model, texts: List[str]) -> np.ndarray:
    arr = model.encode(texts, convert_to_numpy=True)
    return np.asarray(arr, dtype="float32")


def cosine_similarity(a: np.ndarray, b: np.ndarray):
    # a: (d,), b: (n, d)
    a = a / np.linalg.norm(a) if np.linalg.norm(a) != 0 else a
    b_norm = np.linalg.norm(b, axis=1)
    b_safe = b / b_norm[:, None]
    sims = np.dot(b_safe, a)
    return sims


@app.on_event("startup")
def startup():
    global model, conn
    conn = get_conn()
    ensure_table(conn)

    if SentenceTransformer is None:
        raise RuntimeError("Dependência sentence-transformers não encontrada. Instale com: pip install sentence-transformers")
    model = SentenceTransformer("all-MiniLM-L6-v2")


@app.post("/add")
def add_doc(req: AddRequest):
    cur = conn.cursor()
    emb = embed_text(model, [req.text])[0].tolist()
    cur.execute(
        "INSERT OR REPLACE INTO docs (id, text, metadata, embedding) VALUES (?, ?, ?, ?)",
        (req.id, req.text, json.dumps(req.metadata or {}, ensure_ascii=False), json.dumps(emb)),
    )
    conn.commit()
    return {"ok": True, "id": req.id}


@app.post("/search")
def search(req: SearchRequest):
    cur = conn.cursor()
    cur.execute("SELECT id, text, metadata, embedding FROM docs")
    rows = cur.fetchall()
    if not rows:
        return {"results": []}

    # carregar embeddings
    ids = []
    texts = []
    metas = []
    embs = []
    for r in rows:
        ids.append(r[0])
        texts.append(r[1])
        try:
            metas.append(json.loads(r[2]) if r[2] else {})
        except Exception:
            metas.append({})
        try:
            embs.append(np.array(json.loads(r[3]), dtype="float32"))
        except Exception:
            embs.append(np.zeros((model.get_sentence_embedding_dimension(),), dtype="float32"))

    matrix = np.vstack(embs)
    q_emb = embed_text(model, [req.query])[0]
    sims = cosine_similarity(q_emb, matrix)
    top_idx = np.argsort(-sims)[: req.k]

    results = []
    for idx in top_idx:
        results.append({"id": ids[int(idx)], "text": texts[int(idx)], "metadata": metas[int(idx)], "score": float(sims[int(idx)])})

    return {"results": results}


@app.get("/list")
def list_ids():
    cur = conn.cursor()
    cur.execute("SELECT id FROM docs")
    rows = cur.fetchall()
    return {"ids": [r[0] for r in rows]}


@app.post("/delete")
def delete(req: DeleteRequest):
    cur = conn.cursor()
    cur.execute("DELETE FROM docs WHERE id = ?", (req.id,))
    conn.commit()
    return {"ok": True}


if __name__ == "__main__":
    try:
        import uvicorn

        uvicorn.run("mcp_server:app", host="127.0.0.1", port=8000, reload=False)
    except Exception as e:
        print("uvicorn não disponível ou falha ao iniciar servidor:", e)
        print("Você pode instalar uvicorn: pip install uvicorn[standard] e executar: python mcp_server.py")
