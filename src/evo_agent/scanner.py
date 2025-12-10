import os
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .tokenizer import count_tokens

def _match_globs(path: Path, patterns: List[str]) -> bool:
    if not patterns:
        return False
    for pat in patterns:
        if path.match(pat):
            return True
    return False

def _process_file(root_path: Path, p: Path) -> Dict:
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        content = ""
    try:
        stat = p.stat()
        size = stat.st_size
        mtime = stat.st_mtime
    except Exception:
        size = 0
        mtime = 0.0
    rel = p.relative_to(root_path)
    return {
        "path": str(rel).replace("\\", "/"),
        "abs_path": str(p),
        "content": content,
        "size": size,
        "mtime": mtime,
        "tokens": count_tokens(content)
    }

def scan_project(root: str,
                 include_exts: Tuple[str, ...],
                 exclude_globs: List[str],
                 num_workers: int = 10) -> List[Dict]:
    """
    多线程扫描并加载文件内容与 token 计数。
    - 先构建候选文件列表（过滤扩展名与排除规则）
    - 再用 ThreadPoolExecutor 并行读取与计数
    """
    root_path = Path(root).resolve()
    candidates: List[Path] = []
    for p in root_path.rglob("*"):
        if not p.is_file():
            continue
        if include_exts and not any(str(p).lower().endswith(ext) for ext in include_exts):
            continue
        rel = p.relative_to(root_path)
        if _match_globs(rel, exclude_globs):
            continue
        candidates.append(p)

    docs: List[Dict] = []
    if not candidates:
        return docs

    workers = max(1, int(num_workers or 10))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_process_file, root_path, p) for p in candidates]
        for fut in as_completed(futures):
            try:
                docs.append(fut.result())
            except Exception:
                # 忽略单个文件错误，继续
                continue
    return docs