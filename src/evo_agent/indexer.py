import ast
import re
from pathlib import Path
from typing import Dict, List

PY_FUNC_RE = re.compile(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
TS_FUNC_RE = re.compile(r"(?:export\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
TS_CLASS_RE = re.compile(r"(?:export\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)\s*")
JAVA_CLASS_RE = re.compile(r"(?:public|private|protected)?\s*class\s+([A-Za-z_][A-Za-z0-9_]*)")
SQL_TABLE_RE = re.compile(r"CREATE\s+TABLE\s+`?([A-Za-z0-9_]+)`?", re.IGNORECASE)

def index_symbols(docs: List[Dict]) -> List[Dict]:
    symbols: List[Dict] = []
    for d in docs:
        path = d["path"]
        text = d["content"]
        if path.endswith(".py"):
            try:
                tree = ast.parse(text)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        symbols.append({"type": "function", "name": node.name, "path": path})
                    if isinstance(node, ast.ClassDef):
                        symbols.append({"type": "class", "name": node.name, "path": path})
            except Exception:
                # fallback regex
                for m in PY_FUNC_RE.finditer(text):
                    symbols.append({"type": "function", "name": m.group(1), "path": path})
        elif path.endswith((".ts", ".tsx", ".js", ".jsx")):
            for m in TS_FUNC_RE.finditer(text):
                symbols.append({"type": "function", "name": m.group(1), "path": path})
            for m in TS_CLASS_RE.finditer(text):
                symbols.append({"type": "class", "name": m.group(1), "path": path})
        elif path.endswith(".java"):
            for m in JAVA_CLASS_RE.finditer(text):
                symbols.append({"type": "class", "name": m.group(1), "path": path})
        elif path.endswith(".sql"):
            for m in SQL_TABLE_RE.finditer(text):
                symbols.append({"type": "table", "name": m.group(1), "path": path})
    return symbols

def build_tree(docs: List[Dict]) -> str:
    # 生成简单目录树文本
    paths = sorted([d["path"] for d in docs])
    out = []
    last_parts = []
    for p in paths:
        parts = p.split("/")
        # 计算缩进
        prefix = "  " * (len(parts) - 1)
        out.append(f"{prefix}- {parts[-1]}")
    return "\n".join(out)