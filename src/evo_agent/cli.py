import json
import click
from pathlib import Path

from .scanner import scan_project
from .indexer import index_symbols, build_tree
from .selector import select_files
from .compressor import compress_files
from .assembler import assemble_spec, DEFAULT_SYSTEM
from .mistakes import save_mistake, find_relevant
from .connectors import call_llm
from .applier import apply_changes

def _load_yaml(config_path: str):
    import yaml
    if not Path(config_path).exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

@click.group()
def main():
    """Evolutionary Prompt Manager CLI"""
    pass

@main.command()
@click.option("--project", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--task", required=True, type=str)
@click.option("--config", default="configs/evo_config.yaml", type=click.Path(exists=False))
@click.option("--output", default="artifacts/spec.md", type=click.Path())
@click.option("--num-workers", default=None, type=int, help="override thread workers for scanning")
def plan(project, task, config, output, num_workers):
    """生成可审核的规范化 Spec 文档（多线程扫描）"""
    cfg = {
        "include_exts": [".py",".java",".kt",".go",".js",".ts",".tsx",".jsx",".vue",".sql",".md",".json"],
        "exclude_globs": ["node_modules/**",".git/**",".venv/**","**/*.min.js","**/dist/**","**/.DS_Store"],
        "max_context_tokens": 8000,
        "token_budget": 16000,
        "compress_token_limit_per_file": 3000,
        "num_workers": 10
    }
    cfg.update(_load_yaml(config) or {})
    if num_workers is not None:
        cfg["num_workers"] = num_workers

    artifacts = Path("artifacts"); artifacts.mkdir(exist_ok=True)

    docs = scan_project(project, tuple(cfg["include_exts"]), cfg["exclude_globs"], num_workers=cfg["num_workers"])
    symbols = index_symbols(docs)
    tree_text = build_tree(docs)
    symbol_lines = [f"- [{s['type']}] {s['name']} @ {s['path']}" for s in symbols][:500]
    symbol_summary = "\n".join(symbol_lines)

    selected = select_files(docs, task, max_context_tokens=cfg["max_context_tokens"])
    compressed = compress_files(selected, per_file_limit_tokens=cfg["compress_token_limit_per_file"])
    spec, tokens = assemble_spec(project, task, tree_text, symbol_summary, compressed,
                                 system_prompt=DEFAULT_SYSTEM, token_budget=cfg["token_budget"])

    Path(output).write_text(spec, encoding="utf-8")
    click.echo(f"[Spec tokens]: {tokens}")
    click.echo(f"Spec saved to {output}")

@main.command()
@click.option("--project", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--spec", required=True, type=click.Path(exists=True))
@click.option("--provider", required=True, type=click.Choice(["openai","anthropic"]))
@click.option("--model", required=True, type=str)
@click.option("--output", default="artifacts/llm_response.txt", type=click.Path())
def submit(project, spec, provider, model, output):
    """审核通过后，将 Spec 提交给 LLM，保存响应"""
    prompt = Path(spec).read_text(encoding="utf-8")
    resp_text, info = call_llm(provider, model, prompt)
    Path(output).write_text(resp_text, encoding="utf-8")
    click.echo(f"Response saved to {output} [{info}]")

@main.command()
@click.option("--project", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--resp", required=True, type=click.Path(exists=True))
@click.option("--git-commit", is_flag=True, default=False)
def apply(project, resp, git_commit):
    """应用 LLM 返回的文件块或补丁到仓库"""
    text = Path(resp).read_text(encoding="utf-8")
    res = apply_changes(text, project_root=project, git_commit=git_commit)
    click.echo(json.dumps(res, ensure_ascii=False, indent=2))

@main.command()
@click.option("--project", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--task", required=True, type=str)
@click.option("--result", type=click.Choice(["y","n"]), required=True)
@click.option("--reason", default="", type=str)
@click.option("--correction", default="", type=str)
def feedback(project, task, result, reason, correction):
    """记录一次反馈（错题本）"""
    if result == "n" and not reason:
        raise click.UsageError("When result=n, --reason is required.")
    if result == "n":
        entry = save_mistake(project, task=task, reason=reason, correction=correction)
        click.echo("Saved failure:\n" + json.dumps(entry, ensure_ascii=False, indent=2))
    else:
        click.echo("Positive feedback noted (no record persisted).")

@main.command(name="memory")
@click.option("--project", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--task", required=True, type=str)
@click.option("--topk", default=5, type=int)
def list_memory(project, task, topk):
    """查看与任务相关的历史错误提醒"""
    rel = find_relevant(project, task, max_items=topk)
    click.echo(json.dumps(rel, ensure_ascii=False, indent=2))