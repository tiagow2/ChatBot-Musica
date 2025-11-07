import os
import json
import sqlite3
from typing import List, Dict, Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    import faiss
except Exception:
    faiss = None


class LocalAgent:
    """Agente local simples para indexação e busca semântica de textos.

    Implementação leve usando sentence-transformers para embeddings e FAISS para
    busca por similaridade. Persiste o índice FAISS em arquivo e os metadados em
    um banco SQLite local.
    """

    def __init__(self, data_dir: str = "./local_agent_data", model_name: str = "all-MiniLM-L6-v2"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.index_path = os.path.join(self.data_dir, "faiss.index")
        self.db_path = os.path.join(self.data_dir, "metadata.db")

        if SentenceTransformer is None:
            raise ImportError("sentence-transformers não está instalado. Execute: pip install sentence-transformers")
        self.model = SentenceTransformer(model_name)

        # Conectar SQLite
        self.conn = sqlite3.connect(self.db_path)
        self._ensure_table()

        # Carregar/Inicializar FAISS
        self.index = None
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.next_vector_idx = 0
        if faiss is None:
            raise ImportError("faiss não está instalado. Execute: pip install faiss-cpu")

        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                self._refresh_next_idx()
            except Exception:
                # se falhar ao ler, recriaremos
                self.index = None

    def _ensure_table(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS docs (
                id TEXT PRIMARY KEY,
                text TEXT,
                metadata TEXT,
                vector_idx INTEGER
            )
            """
        )
        self.conn.commit()

    def _refresh_next_idx(self):
        cur = self.conn.cursor()
        cur.execute("SELECT MAX(vector_idx) FROM docs")
        r = cur.fetchone()[0]
        self.next_vector_idx = (r + 1) if r is not None else 0

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict] = None):
        """Adiciona um documento ao índice e persiste seus metadados.

        Args:
            doc_id: identificador único do documento
            text: texto a ser indexado
            metadata: dicionário serializável com metadados
        """
        if metadata is None:
            metadata = {}

        emb = self.model.encode([text], convert_to_numpy=True)
        emb = np.asarray(emb, dtype="float32")

        if self.index is None:
            # IndexFlatL2 é simples e funciona bem para protótipos
            self.index = faiss.IndexFlatL2(self.dimension)

        self.index.add(emb)

        vector_idx = self.next_vector_idx
        self.next_vector_idx += 1

        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO docs (id, text, metadata, vector_idx) VALUES (?, ?, ?, ?)",
            (doc_id, text, json.dumps(metadata, ensure_ascii=False), vector_idx),
        )
        self.conn.commit()

        # persistir índice a cada alteração simples
        self.save()

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Retorna até k documentos mais similares ao query.

        Cada item retornado é um dicionário com chaves: id, text, metadata, score.
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        q_emb = self.model.encode([query], convert_to_numpy=True).astype("float32")
        D, I = self.index.search(q_emb, k)
        results = []
        cur = self.conn.cursor()
        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            cur.execute("SELECT id, text, metadata FROM docs WHERE vector_idx = ?", (int(idx),))
            row = cur.fetchone()
            if not row:
                continue
            doc_id, text, meta_json = row
            try:
                meta = json.loads(meta_json) if meta_json else {}
            except Exception:
                meta = {}
            results.append({"id": doc_id, "text": text, "metadata": meta, "score": float(score)})

        return results

    def save(self):
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)

    def close(self):
        try:
            self.save()
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    # pequena demonstração local
    a = LocalAgent()
    a.add_document("ex1", "Esta é a letra de uma música de exemplo.", {"title": "Exemplo"})
    res = a.search("letra música exemplo", k=2)
    print(res)
