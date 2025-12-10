import math
from typing import List, Dict

def _overlap_score(query: str, text: str) -> float:
    qset = set(query.lower().split())
    words = text.lower().split()
    if not words: return 0.0
    overlap = sum(1 for w in words if w in qset)
    return overlap / max(1.0, math.sqrt(len(words)))

def select_files(docs: List[Dict], query: str, max_context_tokens: int) -> List[Dict]:
    qset = set(query.lower().split())
    scored = []
    for d in docs:
        name_boost = 2.0 if any(tok in d["path"].lower() for tok in qset) else 1.0
        s = name_boost * _overlap_score(query, d["content"])
        if s > 0:
            scored.append((s, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected, used = [], 0
    for s, d in scored:
        if used + d["tokens"] > max_context_tokens:
            continue
        selected.append(d)
        used += d["tokens"]
    return selected