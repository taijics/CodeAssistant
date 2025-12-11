// Lightweight JS to drive the UI: file tree loading, modal search, save spec (client-side)
document.addEventListener("DOMContentLoaded", () => {
  // file tree
  const btnFiles = document.getElementById("btn-open-files");
  const fileTreeEl = document.getElementById("file-tree");
  const fileFilter = document.getElementById("file-filter");
  const pid = window.EVO_PROJECT_ID;

  async function loadFileTree() {
    fileTreeEl.innerHTML = "加载文件列表...";
    try {
      const res = await fetch(`/projects/${pid}/files`);
      if (!res.ok) throw new Error("load failed");
      const files = await res.json();
      renderTree(files);
    } catch (err) {
      fileTreeEl.innerHTML = `<div class="empty">无法加载文件：${err.message}</div>`;
    }
  }

  function renderTree(files) {
    // build a nested tree object
    const root = {};
    files.forEach(f => {
      const parts = f.path.split("/");
      let cur = root;
      parts.forEach((p, idx) => {
        if (!cur[p]) cur[p] = {__meta: null, __children: {}};
        if (idx === parts.length - 1) cur[p].__meta = {path: f.path, size: f.size};
        cur = cur[p].__children;
      });
    });

    function nodeToHtml(obj) {
      const ul = document.createElement("ul");
      Object.keys(obj).sort().forEach(k => {
        const item = obj[k];
        const li = document.createElement("li");
        const text = document.createElement("span");
        text.textContent = k + (item.__meta && item.__meta.path ? "" : "/");
        text.className = item.__meta && item.__meta.path ? "file-name" : "folder-name";
        li.appendChild(text);
        if (item.__meta && item.__meta.path) {
          const meta = document.createElement("div");
          meta.className = "path muted";
          meta.textContent = item.__meta.path;
          li.appendChild(meta);
          text.addEventListener("click", () => {
            fetchFileContent(item.__meta.path);
          });
        }
        const childrenKeys = Object.keys(item.__children);
        if (childrenKeys.length) {
          li.appendChild(nodeToHtml(item.__children));
        }
        ul.appendChild(li);
      });
      return ul;
    }

    fileTreeEl.innerHTML = "";
    fileTreeEl.appendChild(nodeToHtml(root));
  }

  async function fetchFileContent(path) {
    try {
      const res = await fetch(`/projects/${pid}/files/read`, {
        method: "POST",
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `path=${encodeURIComponent(path)}`
      });
      if (!res.ok) throw new Error("read failed");
      const j = await res.json();
      const editor = document.getElementById("editor");
      editor.value = `// File: ${j.path}\n\n` + j.content;
      window.scrollTo(0,0);
    } catch (err) {
      alert("读取文件失败：" + err.message);
    }
  }

  // hook buttons
  if (btnFiles) {
    btnFiles.addEventListener("click", () => {
      loadFileTree();
      document.getElementById("file-panel").scrollIntoView({behavior:"smooth"});
    });
  }

  if (fileFilter) {
    fileFilter.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const q = fileFilter.value.trim().toLowerCase();
        // simple client-side filter
        const items = document.querySelectorAll("#file-tree li");
        items.forEach(li => {
          const text = li.textContent.toLowerCase();
          li.style.display = text.includes(q) ? "" : "none";
        });
      }
    });
  }

  // search modal
  const btnSearch = document.getElementById("btn-search");
  const modal = document.getElementById("search-modal");
  const searchInput = document.getElementById("search-input");
  const searchConfirm = document.getElementById("search-confirm");
  const searchCancel = document.getElementById("search-cancel");
  const resultsEl = document.getElementById("search-results");

  if (btnSearch) {
    btnSearch.addEventListener("click", () => {
      modal.setAttribute("aria-hidden","false");
      searchInput.value = "";
      searchInput.focus();
    });
  }
  if (searchCancel) {
    searchCancel.addEventListener("click", () => modal.setAttribute("aria-hidden","true"));
  }
  if (searchConfirm) {
    searchConfirm.addEventListener("click", async () => {
      const q = searchInput.value.trim();
      if (!q) return alert("请输入搜索词");
      // call backend placeholder endpoint
      try {
        const form = new URLSearchParams();
        form.append("query", q);
        const res = await fetch(`/projects/${pid}/search`, {method:"POST", body: form});
        const items = await res.json();
        renderSearchResults(items);
      } catch (err) {
        resultsEl.innerHTML = `<div class="empty">搜索失败：${err.message}</div>`;
      } finally {
        modal.setAttribute("aria-hidden","true");
      }
    });
  }

  function renderSearchResults(items) {
    resultsEl.innerHTML = "";
    if (!items || items.length === 0) {
      resultsEl.innerHTML = `<div class="empty">未找到匹配项（后端搜索功能尚未实现）</div>`;
      return;
    }
    const ul = document.createElement("ul");
    items.forEach(it => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${it.name}</strong> <span class="muted">[${it.type}]</span><div class="path">${it.path}</div><pre>${it.snippet||''}</pre>`;
      li.addEventListener("click", () => {
        // when clicked, load file into editor for editing
        const editor = document.getElementById("editor");
        editor.value = `// ${it.type}: ${it.name} @ ${it.path}\n\n` + (it.snippet || "");
      });
      ul.appendChild(li);
    });
    resultsEl.appendChild(ul);
  }

  // save spec to artifacts/spec.md via a simple POST (not yet implemented server endpoint)
  const btnSave = document.getElementById("btn-save-doc");
  if (btnSave) {
    btnSave.addEventListener("click", async () => {
      const editor = document.getElementById("editor");
      const text = editor.value;
      try {
        const res = await fetch(`/projects/${pid}/artifacts/spec.md`, { method: "PUT", body: text });
        if (res.ok) {
          alert("已保存到 artifacts/spec.md");
        } else {
          alert("保存失败（后端未实现 PUT）");
        }
      } catch (err) {
        alert("保存失败：" + err.message);
      }
    });
  }

  // initial load: try to populate file tree lightly
  // loadFileTree();
});