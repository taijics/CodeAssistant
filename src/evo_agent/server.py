from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import uvicorn

from .project_registry import list_projects, add_project, get_project, update_project, remove_project
from .scanner import scan_project
from .indexer import index_symbols, build_tree
from .selector import select_files
from .compressor import compress_files
from .assembler import assemble_spec, DEFAULT_SYSTEM
from .connectors import call_llm
from .applier import apply_changes

TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"])
)

DEFAULT_CFG = {
    "include_exts": [".py",".java",".kt",".go",".js",".ts",".tsx",".jsx",".vue",".sql",".md",".json"],
    "exclude_globs": ["node_modules/**",".git/**",".venv/**","**/*.min.js","**/dist/**","**/.DS_Store"],
    "max_context_tokens": 8000,
    "token_budget": 16000,
    "compress_token_limit_per_file": 3000,
    "num_workers": 10
}

app = FastAPI(title="Evo Agent UI")

# Serve artifacts directory paths dynamically per project via route

def render(name: str, **ctx):
    tpl = env.get_template(name)
    return HTMLResponse(tpl.render(**ctx))

@app.get("/")
def index():
    projs = list_projects()
    return render("index.html", projects=projs)

@app.post("/projects")
def create_project(name: str = Form(...), root: str = Form(...)):
    add_project(name=name, root=root, config={})
    return RedirectResponse(url="/", status_code=303)

@app.get("/projects/{pid}")
def project_detail(pid: str):
    proj = get_project(pid)
    if not proj:
        return RedirectResponse(url="/", status_code=302)
    root = proj["root"]
    artifacts = Path(root) / ".evo_agent" / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    spec_path = artifacts / "spec.md"
    resp_path = artifacts / "llm_response.txt"
    return render("project_detail.html",
                  project=proj,
                  has_spec=spec_path.exists(),
                  has_resp=resp_path.exists())

@app.post("/projects/{pid}/config")
def update_config(pid: str,
                  max_context_tokens: int = Form(DEFAULT_CFG["max_context_tokens"]),
                  token_budget: int = Form(DEFAULT_CFG["token_budget"]),
                  num_workers: int = Form(DEFAULT_CFG["num_workers"])):
    proj = get_project(pid)
    if not proj:
        return RedirectResponse(url="/", status_code=302)
    cfg = proj.get("config", {})
    cfg.update({
        "max_context_tokens": int(max_context_tokens),
        "token_budget": int(token_budget),
        "num_workers": int(num_workers)
    })
    update_project(pid, {"config": cfg})
    return RedirectResponse(url=f"/projects/{pid}", status_code=303)

@app.post("/projects/{pid}/plan")
def plan(pid: str, task: str = Form(...)):
    proj = get_project(pid)
    if not proj:
        return RedirectResponse(url="/", status_code=302)
    root = proj["root"]
    cfg = {**DEFAULT_CFG, **(proj.get("config") or {})}

    docs = scan_project(root, tuple(cfg["include_exts"]), cfg["exclude_globs"], num_workers=cfg["num_workers"])
    symbols = index_symbols(docs)
    tree_text = build_tree(docs)
    symbol_lines = [f"- [{s['type']}] {s['name']} @ {s['path']}" for s in symbols][:500]
    symbol_summary = "\n".join(symbol_lines)

    selected = select_files(docs, task, max_context_tokens=cfg["max_context_tokens"])
    compressed = compress_files(selected, per_file_limit_tokens=cfg["compress_token_limit_per_file"])
    spec, tokens = assemble_spec(root, task, tree_text, symbol_summary, compressed,
                                 system_prompt=DEFAULT_SYSTEM, token_budget=cfg["token_budget"])

    artifacts = Path(root) / ".evo_agent" / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "spec.md").write_text(spec, encoding="utf-8")

    return RedirectResponse(url=f"/projects/{pid}", status_code=303)

@app.get("/projects/{pid}/artifacts/{fname}")
def get_artifact(pid: str, fname: str):
    proj = get_project(pid)
    if not proj:
        return RedirectResponse(url="/", status_code=302)
    f = Path(proj["root"]) / ".evo_agent" / "artifacts" / fname
    if not f.exists():
        return RedirectResponse(url=f"/projects/{pid}", status_code=302)
    return FileResponse(str(f))

@app.post("/projects/{pid}/submit")
def submit(pid: str,
           provider: str = Form(...),
           model: str = Form(...)):
    proj = get_project(pid)
    if not proj:
        return RedirectResponse(url="/", status_code=302)
    artifacts = Path(proj["root"]) / ".evo_agent" / "artifacts"
    spec = artifacts / "spec.md"
    if not spec.exists():
        return RedirectResponse(url=f"/projects/{pid}", status_code=302)

    prompt = spec.read_text(encoding="utf-8")
    resp_text, info = call_llm(provider, model, prompt)
    (artifacts / "llm_response.txt").write_text(resp_text, encoding="utf-8")
    return RedirectResponse(url=f"/projects/{pid}", status_code=303)

@app.post("/projects/{pid}/apply")
def apply(pid: str, git_commit: Optional[str] = Form(None)):
    proj = get_project(pid)
    if not proj:
        return RedirectResponse(url="/", status_code=302)
    artifacts = Path(proj["root"]) / ".evo_agent" / "artifacts"
    resp = artifacts / "llm_response.txt"
    if not resp.exists():
        return RedirectResponse(url=f"/projects/{pid}", status_code=302)
    text = resp.read_text(encoding="utf-8")
    apply_changes(text, project_root=proj["root"], git_commit=bool(git_commit))
    return RedirectResponse(url=f"/projects/{pid}", status_code=303)

def run():
    uvicorn.run(app, host="127.0.0.1", port=8000)