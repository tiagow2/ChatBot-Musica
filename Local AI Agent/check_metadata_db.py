import sqlite3
from pathlib import Path

p = Path("Local AI Agent/local_agent_data/metadata.db")
print("DB exists:", p.exists())
if not p.exists():
    raise SystemExit("Arquivo metadata.db não encontrado")

conn = sqlite3.connect(p)
cur = conn.cursor()
cur.execute("SELECT id, substr(text,1,200) as preview, metadata, vector_idx FROM docs LIMIT 50")
rows = cur.fetchall()
for r in rows:
    print("ID:", r[0])
    print("Preview:", r[1])
    print("Metadata:", r[2])
    print("vector_idx:", r[3])
    print("-" * 40)
conn.close()