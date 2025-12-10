from typing import List, Dict, Tuple, Optional
from .tokenizer import count_tokens
from .mistakes import find_relevant

DEFAULT_SYSTEM = (
    "You are a senior software engineer. "
    "Provide file-level patches, reasoning, dependency impacts, and at least one test suggestion."
)

def assemble_spec(project_root: str,
                  user_instruction: str,
                  project_tree: str,
                  symbol_summary: str,
                  selected_files: List[Dict],
                  system_prompt: str = DEFAULT_SYSTEM,
                  token_budget: int = 16000,
                  include_mistakes: bool = True) -> Tuple[str, int]:
    system = system_prompt
    if include_mistakes:
        rel = find_relevant(project_root, user_instruction, max_items=5)
        if rel:
            notes = "\n".join([f"- {r['reason']} (correction: {r.get('correction','')})" for r in rel])
            system = system + "\n\n[Historical Warnings]\n" + notes + "\nPlease avoid these mistakes."

    blocks: List[str] = []
    used = count_tokens(system) + count_tokens(user_instruction)
    blocks.append("Project Tree:\n" + project_tree)
    used += count_tokens(project_tree)
    if symbol_summary:
        blocks.append("Symbol Index (functions/classes/tables):\n" + symbol_summary)
        used += count_tokens(symbol_summary)

    for f in selected_files:
        block = f"=== File: {f['path']} ===\n{f['content']}\n"
        t = count_tokens(block)
        if used + t > token_budget:
            break
        blocks.append(block)
        used += t

    spec = (
        f"# System\n{system}\n\n"
        f"# Instruction\n{user_instruction}\n\n"
        f"# Context Blocks\n" + "\n----\n".join(blocks) + "\n\n"
        f"# Output Requirements\n"
        f"- Return code edits as file blocks using the format:\n"
        f"```evoedit\nFILE: relative/path/to/file.ext\n<full file content>\n===END===\n```\n"
        f"- Alternatively, you may return a unified diff patch.\n"
        f"- Ensure error handling (try-except or equivalent) and at least one test suggestion.\n"
    )
    return spec, used