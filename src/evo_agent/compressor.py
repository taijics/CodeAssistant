from typing import List, Dict
from .tokenizer import count_tokens

def compress_files(selected: List[Dict], per_file_limit_tokens: int = 3000) -> List[Dict]:
    out: List[Dict] = []
    for d in selected:
        if d["tokens"] <= per_file_limit_tokens:
            out.append(d)
            continue
        lines = d["content"].splitlines()
        head = "\n".join(lines[:200])
        tail = "\n".join(lines[-200:])
        snippet = head + "\n...\n" + tail
        out.append({
            **d,
            "content": snippet,
            "tokens": count_tokens(snippet)
        })
    return out