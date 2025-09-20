import os, json, math
from typing import List, Dict, Any, Tuple
from app.config import settings

class KBStore:
    _instance = None

    def __init__(self):
        self.catalog_path = "data/catalog.json"
        self.biases_path = "data/biases.json"
        self.embed_model = settings.embed_model
        self._services: List[Dict[str, Any]] = []
        self._biases: List[Dict[str, Any]] = []
        self._embeddings: List[Tuple[str, List[float]]] = []  # (id, vector)

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = KBStore()
        return cls._instance

    def warm(self, force: bool=False):
        if self._services and not force:
            return
        with open(self.catalog_path, "r") as f:
            self._services = json.load(f)["services"]
        with open(self.biases_path, "r") as f:
            self._biases = json.load(f)["biases"]
        self._build_embeddings()

    def _build_embeddings(self):
        # Single pass embedding for services + biases
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

        corpus = []
        for s in self._services:
            txt = f"{s['name']} | {s['category']} | {s.get('description','')}"
            corpus.append(("svc:"+s["service_id"], txt))
        for b in self._biases:
            txt = f"{b['name']} | {b['definition']} | patterns: {';'.join(b.get('copy_patterns',[]))}"
            corpus.append(("bias:"+b["key"], txt))

        if client:
            chunks = [c[1] for c in corpus]
            em = client.embeddings.create(model=self.embed_model, input=chunks)
            self._embeddings = [(corpus[i][0], em.data[i].embedding) for i in range(len(corpus))]
        else:
            # Dev fallback: zero vectors
            self._embeddings = [(cid, [0.0]*1536) for cid,_ in corpus]

    def search(self, query: str, k: int=8) -> List[Dict[str, Any]]:
        vec_q = self._embed_text(query)
        scored = []
        for cid, vec in self._embeddings:
            sim = self._cosine(vec_q, vec)
            scored.append((sim, cid))
        scored.sort(reverse=True)
        out = []
        for _, cid in scored[:k]:
            if cid.startswith("svc:"):
                sid = cid.split("svc:",1)[1]
                item = next((s for s in self._services if s["service_id"]==sid), None)
                if item: out.append({"type":"service","item":item})
            else:
                key = cid.split("bias:",1)[1]
                item = next((b for b in self._biases if b["key"]==key), None)
                if item: out.append({"type":"bias","item":item})
        return out

    def _embed_text(self, text: str) -> List[float]:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        if client:
            em = client.embeddings.create(model=settings.embed_model, input=[text])
            return em.data[0].embedding
        return [0.0]*1536

    @property
    def services(self): return self._services

    @property
    def biases(self): return self._biases

    @property
    def service_by_id(self):
        return {s["service_id"]: s for s in self._services}

    @property
    def bias_by_key(self):
        return {b["key"]: b for b in self._biases}
