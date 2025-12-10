import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict

FILE_BLOCK_RE = re.compile(r"```evoedit\s+FILE:\s*(.+?)\s*\n(.*?)\n===END===\s*```", re.DOTALL)
DIFF_START_RE = re.compile(r"^---\s", re.MULTILINE)

def _apply_file_blocks(resp_text: str, project_root: str) -> List[str]:
    updated: List[str] = []
    for m in FILE_BLOCK_RE.finditer(resp_text):
        rel = m.group(1).strip()
        content = m.group(2)
        target = Path(project_root) / rel
        os.makedirs(target.parent, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        updated.append(rel)
    return updated

def _apply_unified_diff(resp_text: str, project_root: str) -> List[str]:
    # Try to run `patch` tool if available
    try:
        proc = subprocess.run(
            ["patch", "-p0", "-t", "-N", "-r", "-", "-d", project_root],
            input=resp_text.encode("utf-8"),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )
        # We cannot easily list updated files; return empty marker
        return []
    except Exception:
        return []

def apply_changes(resp_text: str, project_root: str, git_commit: bool = False, commit_msg: str = "Apply LLM edits") -> Dict:
    updated_files = _apply_file_blocks(resp_text, project_root)
    if not updated_files and DIFF_START_RE.search(resp_text):
        _apply_unified_diff(resp_text, project_root)

    if git_commit:
        try:
            subprocess.run(["git", "-C", project_root, "add", "."], check=True)
            subprocess.run(["git", "-C", project_root, "commit", "-m", commit_msg], check=True)
        except Exception:
            pass
    return {"updated_files": updated_files}