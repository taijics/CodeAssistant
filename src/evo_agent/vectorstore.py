from typing import List, Dict, Optional

def have_chroma():
    try:
        import chromadb  # noqa
        return True
    except Exception:
        return False

class VectorStore:
    def __init__(self, persist_path: str):
        self.enabled = have_chroma()
        self.db = None
        if self.enabled:
            import chromadb
            self.client = chromadb.PersistentClient(path=persist_path)
            self.coll = self.client.get_or_create_collection("evo_index")
        else:
            self.client = None
            self.coll = None

    def upsert(self, docs: List[Dict]):
        if not self.enabled:
            return
        ids = [d["path"] for d in docs]
        metadatas = [{"path": d["path"]} for d in docs]
        documents = [d["content"] for d in docs]
        self.coll.upsert(ids=ids, metadatas=metadatas, documents=documents)

    def query(self, text: str, top_k: int = 20) -> List[str]:
        if not self.enabled:
            return []
        res = self.coll.query(query_texts=[text], n_results=top_k)
        return res.get("ids", [[]])[0]