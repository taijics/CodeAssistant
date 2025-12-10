import os
import json
import uuid
from typing import Dict, List, Optional

REG_PATH = os.path.join(os.path.expanduser("~"), ".evo_agent")
REG_FILE = os.path.join(REG_PATH, "projects.json")

def _ensure_store():
    os.makedirs(REG_PATH, exist_ok=True)
    if not os.path.exists(REG_FILE):
        with open(REG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def list_projects() -> List[Dict]:
    _ensure_store()
    with open(REG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_project(pid: str) -> Optional[Dict]:
    for p in list_projects():
        if p["id"] == pid:
            return p
    return None

def add_project(name: str, root: str, config: Optional[Dict] = None) -> Dict:
    _ensure_store()
    proj = {
        "id": str(uuid.uuid4()),
        "name": name,
        "root": os.path.abspath(root),
        "config": config or {}
    }
    projs = list_projects()
    projs.append(proj)
    with open(REG_FILE, "w", encoding="utf-8") as f:
        json.dump(projs, f, ensure_ascii=False, indent=2)
    return proj

def update_project(pid: str, patch: Dict) -> Optional[Dict]:
    _ensure_store()
    projs = list_projects()
    out = []
    target = None
    for p in projs:
        if p["id"] == pid:
            p.update(patch)
            target = p
        out.append(p)
    with open(REG_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return target

def remove_project(pid: str) -> bool:
    _ensure_store()
    projs = list_projects()
    out = [p for p in projs if p["id"] != pid]
    with open(REG_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return len(out) != len(projs)