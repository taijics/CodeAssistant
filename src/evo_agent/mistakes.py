import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional

def _store_path(project_root: str) -> str:
    d = os.path.join(project_root, ".evo_agent")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "mistakes.json")

def load_mistakes(project_root: str) -> List[Dict]:
    path = _store_path(project_root)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_mistake(project_root: str,
                 task: str,
                 reason: str,
                 correction: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 related_files: Optional[List[str]] = None,
                 context_snippet: Optional[str] = None) -> Dict:
    entry = {
        "id": str(uuid.uuid4()),
        "task": task,
        "reason": reason,
        "correction": correction or "",
        "tags": tags or [],
        "related_files": related_files or [],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "context_snippet": context_snippet or ""
    }
    records = load_mistakes(project_root)
    records.append(entry)
    with open(_store_path(project_root), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return entry

def find_relevant(project_root: str, task_query: str, max_items: int = 5) -> List[Dict]:
    records = load_mistakes(project_root)
    qset = set(task_query.lower().split())
    def score(r):
        text = (r.get("reason","") + " " + r.get("task","") + " " + " ".join(r.get("tags",[]))).lower()
        return len(qset & set(text.split()))
    ranked = sorted(records, key=score, reverse=True)
    return ranked[:max_items]