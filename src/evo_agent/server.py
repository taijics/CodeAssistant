from pathlib import Path
from typing import Optional, Dict, Any, List
import os
import json
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse, JSONResponse
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

# Templates / static
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"])
)

# Create FastAPI app and mount static assets
app = FastAPI(title="Evo Agent UI")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


DEFAULT_CFG = {
    "include_exts": [".py",".java",".kt",".go",".js",".ts",".tsx",".jsx",".vue",".sql",".md",".json"],
    "exclude_globs": ["node_modules/**",".git/**",".venv/**","**/*.min.js","**/dist/**","**/.DS_Store"],
    "max_context_tokens": 8000,
    "token_budget": 16000,
    "compress_token_limit_per_file": 3000,
    "num_workers": 10
}

# Helper render
def render(name: str, **ctx):
    tpl = env.get_template(name)
    return HTMLResponse(tpl.render(**ctx))

@app.get("/")
def index():
    projs = list_projects()
    # Enrich with some computed metadata if available
    enriched = []
    for p in projs:
        root = p.get("root")
        meta = p.copy()
        try:
            # basic stats: file count if previously scanned (artifact), else unknown
            store = Path(root) / ".evo_agent"
            stats_file = store / "project_meta.json"
            if stats_file.exists():
                meta_stats = json.loads(stats_file.read_text(encoding="utf-8"))
                meta.update(meta_stats)
        except Exception:
            pass
        enriched.append(meta)
    return render("index.html", projects=enriched)

@app.post("/projects")
def create_project(name: str = Form(...), root: str = Form(...), description: str = Form("")):
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

    # try load project meta (file counters)
    meta = {}
    try:
        stats_file = Path(root) / ".evo_agent" / "project_meta.json"
        if stats_file.exists():
            meta = json.loads(stats_file.read_text(encoding="utf-8"))
    except Exception:
        meta = {}

    return render("project_detail.html",
                  project=proj,
                  has_spec=spec_path.exists(),
                  has_resp=resp_path.exists(),
                  meta=meta)

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
        raise HTTPException(status_code=404, detail="project not found")
    root = proj["root"]
    cfg = {**DEFAULT_CFG, **(proj.get("config") or {})}

    # perform scan (this may be heavy) - reuse existing scan_project
    docs = scan_project(root, tuple(cfg["include_exts"]), cfg["exclude_globs"], num_workers=cfg["num_workers"])
    symbols = index_symbols(docs)
    tree_text = build_tree(docs)
    symbol_lines = [f"- [{s['type']}] {s['name']} @ {s['path']}" for s in symbols][:500]
    symbol_summary = "\n".join(symbol_lines)

    selected = select_files(docs, task, max_context_tokens=cfg["max_context_tokens"])
    compressed = compress_files(selected, per_file_limit_per_file=cfg["compress_token_limit_per_file"])

    spec, tokens = assemble_spec(root, task, tree_text, symbol_summary, compressed,
                                 system_prompt=DEFAULT_SYSTEM, token_budget=cfg["token_budget"])

    artifacts = Path(root) / ".evo_agent" / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "spec.md").write_text(spec, encoding="utf-8")

    # save some metadata (file count, symbol counts) for display in UI
    try:
        meta = {
            "project_file_count": len(docs),
            "symbol_count": len(symbols),
            "last_plan_tokens": tokens
        }
        (Path(root) / ".evo_agent" / "project_meta.json").write_text(json.dumps(meta), encoding="utf-8")
    except Exception:
        pass

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

@app.get("/projects/{pid}/files")
def project_files(pid: str):
    """
    Return a JSON list of project files as a simple tree structure.
    This endpoint is intentionally lightweight: it enumerates file paths only (no file contents).
    """
    proj = get_project(pid)
    if not proj:
        raise HTTPException(status_code=404, detail="project not found")
    root = Path(proj["root"])
    if not root.exists():
        raise HTTPException(status_code=400, detail="project root not found")
    result = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(root)
            result.append({
                "path": str(rel).replace("\\", "/"),
                "size": p.stat().st_size,
                "mtime": p.stat().st_mtime
            })
        except Exception:
            continue
    return JSONResponse(result)

@app.post("/projects/{pid}/search")
def project_search(pid: str, query: str = Form(...)):
    """
    Placeholder search endpoint.
    For now it returns an empty list; frontend is built to consume a list of entities
    with fields: {'type','name','path','snippet'}.
    Functional implementation will be added later (embeddings/regex/indexer).
    """
    proj = get_project(pid)
    if not proj:
        raise HTTPException(status_code=404, detail="project not found")
    # TODO: implement real search logic later
    return JSONResponse([])

@app.post("/projects/{pid}/files/read")
def read_file(pid: str, path: str = Form(...)):
    proj = get_project(pid)
    if not proj:
        raise HTTPException(status_code=404, detail="project not found")
    root = Path(proj["root"])
    target = root / path
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="file not found")
    content = target.read_text(encoding="utf-8", errors="ignore")
    return JSONResponse({"path": path, "content": content})

def run():
    uvicorn.run(app, host="127.0.0.1", port=8000)