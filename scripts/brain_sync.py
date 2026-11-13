#!/usr/bin/env python3
"""
🧠 Base de Conhecimento Inteligente v2.0 (Antigravity <-> Google NotebookLM)

Caderno Central (Alias: `cerebro`):
  ID: 4e930edb-9f8d-4a41-9987-52a3d1291720
  URL: https://notebook.google.com/notebook/4e930edb-9f8d-4a41-9987-52a3d1291720

Pilares da Base de Conhecimento Inteligente:
  1. Memória Bidirecional (RAG):
     - ask "pergunta"                   Consulta o Segundo Cérebro antes de codar ou tomar decisões
     - cross-ask "pergunta"             Consulta TODOS os cadernos da conta simultaneamente
  2. Memória de Engenharia (ADRs & Bugs):
     - log-adr                          Registra uma Decisão Arquitetural (ADR) no catálogo vivo
     - log-bug                          Registra um Erro Resolvido (Postmortem & Troubleshooting)
  3. Ingestão Inteligente & Auto-Catalogação:
     - sync-chat                        Sincroniza histórico e decisões da conversa com auto-tags
     - sync-code                        Gera documentação profunda de código (dependências + AST + fonte)
     - sync-learning / save-doc         Publica guias de aprendizado estruturados
     - create-notebook                  Cria um caderno NOVO exclusivo para o projeto/conversa
     - sync-index                       Atualiza o '🗂️ Índice Mestre da Base de Conhecimento' no NotebookLM
  4. Gerador Ativo de Estudos (Studio):
     - study-kit                        Gera Quiz, Flashcards, Mapa Mental, Guia ou Podcast no NotebookLM
"""

import argparse
import ast
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

BRAIN_NOTEBOOK_ID = "4e930edb-9f8d-4a41-9987-52a3d1291720"
BRAIN_NOTEBOOK_URL = f"https://notebook.google.com/notebook/{BRAIN_NOTEBOOK_ID}"
NLM_WRAPPER = Path("/home/antigravity/.gemini/nlm/nlm_wrapper.py")
KNOWLEDGE_DIR = Path("/home/antigravity/.gemini/nlm/knowledge")
CATALOG_FILE = KNOWLEDGE_DIR / "catalog.json"
ADRS_FILE = KNOWLEDGE_DIR / "adrs.md"
BUGS_FILE = KNOWLEDGE_DIR / "bugs.md"

EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".next",
    "dist",
    "build",
    ".agents",
}

CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".sh",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
    ".html",
    ".css",
}

TAG_KEYWORDS = {
    "python": ["python", "pytest", "pip", "uv", "fastapi", "flask", "django", "ast", "httpx"],
    "javascript": ["javascript", "node", "npm", "typescript", "vite", "next.js", "react"],
    "frontend": ["html", "css", "tailwind", "ui", "ux", "dashboard", "frontend", "react"],
    "backend": ["api", "rest", "graphql", "servidor", "server", "database", "sql", "backend"],
    "mcp": ["mcp", "model context protocol", "gemini-notebook-mcp", "notebooklm-mcp"],
    "automacao": ["automação", "automacao", "script", "cli", "cron", "pipeline", "brain_sync"],
    "arquitetura": ["arquitetura", "adr", "design pattern", "estrutura", "microserviço", "fuse"],
    "bugfix": ["erro", "bug", "fix", "correção", "troubleshooting", "exception", "falha"],
    "ia": ["ia", "ai", "llm", "gemini", "notebooklm", "prompt", "rag", "agente", "skill"],
}


def ensure_knowledge_dir() -> None:
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    if not CATALOG_FILE.exists():
        CATALOG_FILE.write_text(
            json.dumps(
                {
                    "updated_at": "",
                    "central_notebook_id": BRAIN_NOTEBOOK_ID,
                    "entries": [],
                    "adrs_count": 0,
                    "bugs_count": 0,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


def auto_detect_tags(text: str, extra_tags: list[str] | None = None) -> list[str]:
    lower = text.lower()
    detected = set(extra_tags or [])
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            detected.add(tag)
    if not detected:
        detected.add("geral")
    return sorted(detected)


def record_catalog_entry(
    title: str,
    category: str,
    notebook_id: str,
    tags: list[str],
    summary: str = "",
) -> None:
    ensure_knowledge_dir()
    try:
        catalog = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        catalog = {"updated_at": "", "central_notebook_id": BRAIN_NOTEBOOK_ID, "entries": []}

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    catalog["updated_at"] = now_str

    entries = [
        e
        for e in catalog.get("entries", [])
        if not (e.get("title", "").lower() == title.lower() and e.get("notebook_id") == notebook_id)
    ]
    entries.insert(
        0,
        {
            "title": title,
            "category": category,
            "notebook_id": notebook_id,
            "notebook_url": f"https://notebook.google.com/notebook/{notebook_id}",
            "tags": tags,
            "summary": summary[:280],
            "updated_at": now_str,
        },
    )
    catalog["entries"] = entries
    CATALOG_FILE.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")


def run_nlm(args: list[str], check: bool = True) -> str:
    cmd = [sys.executable, str(NLM_WRAPPER), "cli", *args]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(
            f"Erro ao executar nlm {' '.join(args)}:\n{res.stderr or res.stdout}"
        )
    return (res.stdout or res.stderr or "").strip()


def list_sources(notebook_id: str) -> list[dict]:
    out = run_nlm(["source", "list", notebook_id, "--json"], check=False)
    if not out:
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict) and "sources" in data:
            return data["sources"]
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def list_all_notebooks() -> list[dict]:
    out = run_nlm(["notebook", "list", "--json"], check=False)
    if not out:
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict) and "notebooks" in data:
            return data["notebooks"]
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def upsert_text_source(
    notebook_id: str,
    title: str,
    content: str,
    category: str = "geral",
    summary: str = "",
) -> dict:
    """Adiciona ou atualiza uma fonte de texto no caderno (evitando duplicatas) e registra no catálogo."""
    existing_sources = list_sources(notebook_id)
    matching_ids = [
        s.get("id") or s.get("source_id")
        for s in existing_sources
        if (s.get("title") or "").strip().lower() == title.strip().lower()
    ]

    out = run_nlm(
        [
            "source",
            "add",
            notebook_id,
            "--text",
            content,
            "--title",
            title,
            "--json",
        ]
    )

    for old_id in matching_ids:
        if old_id:
            try:
                run_nlm(["source", "delete", str(old_id), "--confirm"], check=False)
            except Exception:
                pass

    tags = auto_detect_tags(f"{title}\n{content}", [category])
    record_catalog_entry(
        title=title,
        category=category,
        notebook_id=notebook_id,
        tags=tags,
        summary=summary or content.splitlines()[0][:200] if content else title,
    )

    try:
        run_nlm(["tag", "add", notebook_id, "--tags", ",".join(tags[:6])], check=False)
    except Exception:
        pass

    try:
        return json.loads(out)
    except Exception:
        return {"raw": out, "title": title}


def extract_python_symbols(file_path: Path) -> list[str]:
    symbols: list[str] = []
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8", errors="replace"))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or ""
                first_line = doc.splitlines()[0] if doc else ""
                methods = [
                    n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                m_str = f" (métodos: `{', '.join(methods)}`)" if methods else ""
                symbols.append(f"- **Classe `{node.name}`**{m_str}: {first_line}")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node) or ""
                first_line = doc.splitlines()[0] if doc else ""
                args_list = [a.arg for a in node.args.args]
                sig = f"{node.name}({', '.join(args_list)})"
                symbols.append(f"- **Função `{sig}`**: {first_line}")
    except Exception:
        pass
    return symbols


def extract_project_dependencies(target_dir: Path) -> list[str]:
    deps: list[str] = []
    pkg_json = target_dir / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8"))
            for section in ("dependencies", "devDependencies"):
                if section in data and isinstance(data[section], dict):
                    for k, v in data[section].items():
                        deps.append(f"- Node/NPM (`{section}`): `{k}` ({v})")
        except Exception:
            pass

    req_txt = target_dir / "requirements.txt"
    if req_txt.exists():
        for line in req_txt.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                deps.append(f"- Python (`requirements.txt`): `{line}`")

    pyproject = target_dir / "pyproject.toml"
    if pyproject.exists():
        deps.append("- Configuração Python: `pyproject.toml` presente")

    mcp_cfg = target_dir / "mcp_config.json"
    if mcp_cfg.exists():
        try:
            data = json.loads(mcp_cfg.read_text(encoding="utf-8"))
            servers = list((data.get("mcpServers") or {}).keys())
            if servers:
                deps.append(f"- Servidores MCP configurados: `{', '.join(servers)}`")
        except Exception:
            pass

    return deps


def build_code_documentation(target_dir: Path, project_name: str | None = None) -> tuple[str, str]:
    proj = project_name or target_dir.name
    doc_title = f"💻 Documentação de Código — {proj}"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {doc_title}",
        "",
        "Documentação técnica e estrutural gerada automaticamente pela Base de Conhecimento Inteligente do Antigravity.",
        "",
        f"- **Projeto:** `{proj}`",
        f"- **Caminho:** `{target_dir}`",
        f"- **Atualizado em:** {now_str}",
        "",
    ]

    deps = extract_project_dependencies(target_dir)
    if deps:
        lines.append("## 1. Dependências e Integrações Detectadas")
        lines.append("")
        lines.extend(deps)
        lines.append("")

    lines.extend(
        [
            "## 2. Árvore de Diretórios e Arquivos",
            "",
            "```text",
        ]
    )

    code_files: list[Path] = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
        rel_root = Path(root).relative_to(target_dir)
        depth = 0 if str(rel_root) == "." else len(rel_root.parts)
        indent = "  " * depth
        if str(rel_root) != ".":
            lines.append(f"{indent}{rel_root.name}/")
        for f in sorted(files):
            fp = Path(root) / f
            lines.append(f"{indent}  {f}")
            if fp.suffix.lower() in CODE_EXTENSIONS and fp.stat().st_size < 80_000:
                code_files.append(fp)

    lines.append("```")
    lines.append("")
    lines.append("## 3. Mapa de Módulos, Funções e Classes (AST)")
    lines.append("")

    has_symbols = False
    for fp in code_files:
        if fp.suffix.lower() == ".py":
            syms = extract_python_symbols(fp)
            if syms:
                has_symbols = True
                rel = fp.relative_to(target_dir)
                lines.append(f"### `{rel}`")
                lines.extend(syms)
                lines.append("")
    if not has_symbols:
        lines.append("*(Nenhum símbolo Python extraído ou projeto baseado em outros formatos)*")
        lines.append("")

    lines.append("## 4. Código-Fonte e Documentação dos Arquivos")
    lines.append("")

    for fp in code_files:
        rel = fp.relative_to(target_dir)
        ext = fp.suffix.lstrip(".") or "text"
        content = fp.read_text(encoding="utf-8", errors="replace")
        lines.append(f"### Arquivo: `{rel}`")
        lines.append("")
        lines.append(f"```{ext}")
        lines.append(content.rstrip())
        lines.append("```")
        lines.append("")

    return doc_title, "\n".join(lines)


# =========================================================================
# COMANDOS DA BASE DE CONHECIMENTO INTELIGENTE
# =========================================================================


def cmd_ask(args: argparse.Namespace) -> None:
    """Consulta RAG Bidirecional no Segundo Cérebro (ou caderno específico)."""
    print(f"🔍 Consultando a Base de Conhecimento ({args.notebook}): '{args.question}'...\n")
    q_args = ["notebook", "query", args.notebook, args.question]
    if args.new_conversation:
        q_args.append("--new-conversation")
    out = run_nlm(q_args)
    print(out)


def cmd_cross_ask(args: argparse.Namespace) -> None:
    """Consulta transversal em TODOS os cadernos da conta (Cross-Notebook RAG)."""
    print(f"🌐 Consultando TODOS os cadernos da Base de Conhecimento: '{args.question}'...\n")
    q_args = ["cross", "query", args.question]
    if args.tags:
        q_args.extend(["--tags", args.tags])
    else:
        q_args.append("--all")
    out = run_nlm(q_args)
    print(out)


def cmd_log_adr(args: argparse.Namespace) -> None:
    """Registra uma Decisão Arquitetural (ADR) no livro de arquitetura da Base de Conhecimento."""
    ensure_knowledge_dir()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    project = args.project or "Geral / Antigravity"

    header = (
        "# 🏛️ Memória de Arquitetura — Registro de Decisões Técnicas (ADRs)\n\n"
        "Este documento consolida todas as decisões arquiteturais importantes tomadas nos projetos no Antigravity.\n\n---\n\n"
    )
    existing = ADRS_FILE.read_text(encoding="utf-8") if ADRS_FILE.exists() else header

    entry_md = (
        f"## ADR: {args.title}\n"
        f"- **Data:** {now_str}\n"
        f"- **Projeto:** `{project}`\n"
        f"- **Status:** Aceito / Implementado\n"
        f"- **Contexto / Problema:** {args.context}\n"
        f"- **Decisão Tomada:** {args.decision}\n"
        f"- **Consequências e Trade-offs:** {args.consequences or 'Documentado e em produção.'}\n\n---\n\n"
    )

    updated = existing + entry_md
    ADRS_FILE.write_text(updated, encoding="utf-8")

    title = "🏛️ Memória de Arquitetura — Decisões Técnicas (ADRs)"
    print(f"🏛️ Sincronizando ADR '{args.title}' na Base de Conhecimento...")
    upsert_text_source(
        args.notebook,
        title,
        updated,
        category="arquitetura",
        summary=f"ADR ({project}): {args.title} -> {args.decision}",
    )
    print(f"✅ ADR registrado e indexado em {BRAIN_NOTEBOOK_URL}")


def cmd_log_bug(args: argparse.Namespace) -> None:
    """Registra um Bug Resolvido (Postmortem / Troubleshooting) para memória futura."""
    ensure_knowledge_dir()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    project = args.project or "Geral / Antigravity"

    header = (
        "# 🛠️ Catálogo de Soluções de Bugs & Troubleshooting\n\n"
        "Base de conhecimento de erros técnicos encontrados, causas-raiz diagnosticadas e soluções definitivas.\n\n---\n\n"
    )
    existing = BUGS_FILE.read_text(encoding="utf-8") if BUGS_FILE.exists() else header

    entry_md = (
        f"## 🐛 Bug / Problema: {args.title}\n"
        f"- **Data:** {now_str}\n"
        f"- **Projeto:** `{project}`\n"
        f"- **Sintoma / Erro Exato:** {args.symptom}\n"
        f"- **Causa-Raiz:** {args.cause}\n"
        f"- **Solução Definitiva:** {args.solution}\n\n---\n\n"
    )

    updated = existing + entry_md
    BUGS_FILE.write_text(updated, encoding="utf-8")

    title = "🛠️ Catálogo de Soluções de Bugs & Troubleshooting"
    print(f"🛠️ Sincronizando solução de bug '{args.title}' na Base de Conhecimento...")
    upsert_text_source(
        args.notebook,
        title,
        updated,
        category="bugfix",
        summary=f"Bug ({project}): {args.title} -> Solução: {args.solution}",
    )
    print(f"✅ Solução de bug registrada e indexada em {BRAIN_NOTEBOOK_URL}")


def cmd_sync_index(args: argparse.Namespace) -> None:
    """Gera e sincroniza o '🗂️ Índice Mestre — Catálogo da Base de Conhecimento' no Segundo Cérebro."""
    ensure_knowledge_dir()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    notebooks = list_all_notebooks()
    sources = list_sources(args.notebook)

    try:
        catalog = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        catalog = {"entries": []}

    lines = [
        "# 🗂️ Índice Mestre — Catálogo da Base de Conhecimento Inteligente",
        "",
        f"- **Atualizado automaticamente em:** {now_str}",
        f"- **Caderno Central (Segundo Cérebro):** `{BRAIN_NOTEBOOK_ID}` ({BRAIN_NOTEBOOK_URL})",
        "",
        "## 1. Cadernos Ativos na Conta do NotebookLM",
        "",
    ]

    if notebooks:
        for nb in notebooks:
            nb_id = nb.get("id") or nb.get("notebook_id") or ""
            nb_title = nb.get("title") or "Sem título"
            lines.append(f"- **{nb_title}** — ID: `{nb_id}` (https://notebook.google.com/notebook/{nb_id})")
    else:
        lines.append(f"- **Conectar Antigravity com NotebookLM via MCP** — ID: `{BRAIN_NOTEBOOK_ID}`")

    lines.extend(
        [
            "",
            "## 2. Fontes Indexadas no Caderno 'Conectar Antigravity com NotebookLM via MCP'",
            "",
        ]
    )

    for s in sources:
        s_title = s.get("title") or "Sem título"
        s_id = s.get("id") or s.get("source_id") or ""
        if "Índice Mestre" not in s_title:
            lines.append(f"- **{s_title}** (Source ID: `{s_id}`)")

    entries = catalog.get("entries", [])
    if entries:
        lines.extend(
            [
                "",
                "## 3. Histórico de Entradas Catalogadas & Tags",
                "",
            ]
        )
        for e in entries[:30]:
            tags_str = ", ".join(f"`#{t}`" for t in e.get("tags", []))
            lines.append(
                f"- **[{e.get('updated_at', '')}] {e.get('title')}** ({e.get('category')}) — Tags: {tags_str}\n"
                f"  - Resumo: {e.get('summary', '')}"
            )

    lines.extend(
        [
            "",
            "## 4. Guia de Consultas Inteligentes (RAG)",
            "",
            "- Para consultar decisões passadas: `python3 /home/antigravity/.gemini/nlm/brain_sync.py ask \"Quais decisões de arquitetura já tomamos?\"`",
            "- Para consultar erros e bugs já resolvidos: `python3 /home/antigravity/.gemini/nlm/brain_sync.py ask \"Como resolvemos o problema de permissão FUSE ou proxy httpx?\"`",
            "- Para buscar em todos os cadernos ao mesmo tempo: `python3 /home/antigravity/.gemini/nlm/brain_sync.py cross-ask \"Resumo de todos os projetos\"`",
        ]
    )

    content = "\n".join(lines)
    title = "🗂️ Índice Mestre — Catálogo da Base de Conhecimento"
    print("🗂️ Atualizando o Índice Mestre da Base de Conhecimento no NotebookLM...")
    upsert_text_source(
        args.notebook,
        title,
        content,
        category="indice",
        summary="Mapa global de todos os cadernos, fontes, ADRs, bugs resolvidos e tags da Base de Conhecimento.",
    )
    print(f"✅ Índice Mestre sincronizado com sucesso! ({BRAIN_NOTEBOOK_URL})")


def cmd_study_kit(args: argparse.Namespace) -> None:
    """Aciona o Studio do NotebookLM para gerar materiais de estudo (Quiz, Flashcards, Mindmap, Audio, Report)."""
    types = [t.strip().lower() for t in args.types.split(",") if t.strip()]
    focus = (
        f"Foque em: {args.topic}. Use apenas as fontes enviadas neste caderno em português (pt-BR)."
        if args.topic
        else "Sintetize os principais conceitos técnicos, decisões de arquitetura e aprendizados práticos das fontes em português (pt-BR)."
    )

    print(f"🎓 Gerando Kit de Estudos ({', '.join(types)}) no caderno '{args.notebook}'...")
    for t in types:
        try:
            if t == "quiz":
                print("  📝 Solicitação: Quiz interativo (5 questões, nível médio)...")
                run_nlm(["quiz", "create", args.notebook, "--count", "5", "--difficulty", "3", "--focus", focus, "--confirm"])
                print("  ✅ Quiz em geração no NotebookLM Studio!")
            elif t == "flashcards":
                print("  🗂️ Solicitação: Flashcards de fixação...")
                run_nlm(["flashcards", "create", args.notebook, "--difficulty", "medium", "--focus", focus, "--confirm"])
                print("  ✅ Flashcards em geração no NotebookLM Studio!")
            elif t in ("mindmap", "mind_map", "mapa"):
                title = f"Mapa Mental — {args.topic}" if args.topic else "Mapa Mental da Base de Conhecimento"
                print(f"  🧭 Solicitação: Mapa Mental ('{title}')...")
                run_nlm(["mindmap", "create", args.notebook, "--title", title, "--confirm"])
                print("  ✅ Mapa Mental gerado no NotebookLM Studio!")
            elif t in ("report", "guia"):
                print("  📘 Solicitação: Study Guide (Guia de Estudos)...")
                run_nlm(["report", "create", args.notebook, "--format", "Study Guide", "--language", "pt-BR", "--confirm"])
                print("  ✅ Guia de Estudos em geração no NotebookLM Studio!")
            elif t in ("audio", "podcast"):
                print("  🎧 Solicitação: Podcast (Audio Overview em pt-BR)...")
                run_nlm(["audio", "create", args.notebook, "--format", "deep_dive", "--language", "pt-BR", "--focus", focus, "--confirm"])
                print("  ✅ Podcast (Audio Overview) em geração no NotebookLM Studio!")
            else:
                print(f"  ⚠️ Tipo desconhecido ignorado: {t}")
        except Exception as e:
            print(f"  ⚠️ Aviso ao gerar {t}: {e}")

    print(f"\n🔗 Acesse os materiais gerados na aba 'Studio' do seu caderno: {BRAIN_NOTEBOOK_URL}")


def cmd_sync_chat(args: argparse.Namespace) -> None:
    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        content = args.text
    else:
        raise ValueError("Informe --file ou --text com o resumo/histórico da conversa.")

    full_title = (
        args.title
        if args.title.startswith("💬")
        else f"💬 Chat & Decisões — {args.title}"
    )
    print(f"🧠 Sincronizando conversa '{full_title}' para o Segundo Cérebro...")
    upsert_text_source(args.notebook, full_title, content, category="chat", summary=args.title)
    print("✅ Conversa sincronizada com sucesso!")
    print(f"🔗 Caderno: {BRAIN_NOTEBOOK_URL}")


def cmd_sync_code(args: argparse.Namespace) -> None:
    target_dir = Path(args.dir).resolve()
    if not target_dir.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {target_dir}")
    doc_title, md_content = build_code_documentation(target_dir, project_name=args.project)
    print(f"💻 Sincronizando documentação de código '{doc_title}' para o Segundo Cérebro...")
    upsert_text_source(
        args.notebook,
        doc_title,
        md_content,
        category="codigo",
        summary=f"Documentação completa de código e AST do projeto {args.project or target_dir.name}",
    )
    print("✅ Documentação de código sincronizada com sucesso!")
    print(f"🔗 Caderno: {BRAIN_NOTEBOOK_URL}")


def cmd_save_doc(args: argparse.Namespace) -> None:
    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        content = args.text
    else:
        raise ValueError("Informe --file ou --text")

    prefix_map = {
        "aprendizado": "📘 Aprendizado — ",
        "codigo": "💻 Código — ",
        "arquitetura": "🏗️ Arquitetura — ",
        "chat": "💬 Chat & Decisões — ",
    }
    prefix = prefix_map.get(args.category.lower(), "📘 Nota — ")
    full_title = args.title if args.title.startswith(("📘", "💻", "🏗️", "💬")) else f"{prefix}{args.title}"

    print(f"📝 Salvando '{full_title}' no Segundo Cérebro...")
    upsert_text_source(args.notebook, full_title, content, category=args.category.lower(), summary=args.title)
    print("✅ Documento salvo e indexado no NotebookLM!")
    print(f"🔗 Caderno: {BRAIN_NOTEBOOK_URL}")


def cmd_create_notebook(args: argparse.Namespace) -> None:
    title = args.title
    print(f"📓 Criando novo caderno no NotebookLM: '{title}'...")
    out = run_nlm(["notebook", "create", title, "--json"])
    nb_id = None
    try:
        data = json.loads(out)
        nb_id = data.get("id") or data.get("notebook_id")
    except Exception:
        pass
    if not nb_id:
        out_quiet = run_nlm(["notebook", "create", title, "--quiet"])
        nb_id = out_quiet.strip().splitlines()[-1].strip()

    nb_url = f"https://notebook.google.com/notebook/{nb_id}"
    print(f"✅ Caderno criado! ID: {nb_id}")
    print(f"🔗 Link: {nb_url}")

    try:
        run_nlm(["chat", "configure", nb_id, "--goal", "learning_guide"], check=False)
        run_nlm(["chat", "configure", nb_id, "--response-length", "longer"], check=False)
    except Exception:
        pass

    if args.alias:
        try:
            run_nlm(["alias", "set", args.alias, nb_id], check=False)
        except Exception:
            pass

    if args.chat_file:
        chat_content = Path(args.chat_file).read_text(encoding="utf-8")
        upsert_text_source(nb_id, f"💬 Chat & Decisões — {title}", chat_content, category="chat")
        print("  ✓ Fonte de Chat & Decisões adicionada!")

    if args.code_dir:
        target_dir = Path(args.code_dir).resolve()
        doc_title, md_content = build_code_documentation(target_dir, project_name=args.project or title)
        upsert_text_source(nb_id, doc_title, md_content, category="codigo")
        print("  ✓ Fonte de Documentação de Código adicionada!")

    if args.learning_file:
        learn_content = Path(args.learning_file).read_text(encoding="utf-8")
        upsert_text_source(nb_id, f"📘 Aprendizado — {title}", learn_content, category="aprendizado")
        print("  ✓ Fonte de Guia de Aprendizado adicionada!")

    print(f"\n🎉 Novo Notebook pronto: {nb_url}")


def cmd_status(args: argparse.Namespace) -> None:
    nb_url = (
        BRAIN_NOTEBOOK_URL
        if args.notebook in (BRAIN_NOTEBOOK_ID, "cerebro")
        else f"https://notebook.google.com/notebook/{args.notebook}"
    )
    print("=" * 72)
    print("🧠 BASE DE CONHECIMENTO INTELIGENTE — NOTEBOOKLM")
    print(f"🔗 Link: {nb_url}")
    print("=" * 72)
    out = run_nlm(["source", "list", args.notebook])
    print(out)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Base de Conhecimento Inteligente v2.0 (Antigravity <-> NotebookLM)"
    )
    parser.add_argument(
        "--notebook",
        default=BRAIN_NOTEBOOK_ID,
        help="ID ou alias do caderno no NotebookLM (padrão: cerebro)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # 1. RAG Bidirecional
    p_ask = sub.add_parser("ask", help="Consulta inteligente (RAG) na Base de Conhecimento antes de codar")
    p_ask.add_argument("question", help="Pergunta para a Base de Conhecimento")
    p_ask.add_argument("--new-conversation", action="store_true", help="Iniciar nova sessão de pergunta")

    p_cross = sub.add_parser("cross-ask", help="Consulta simultânea em TODOS os cadernos da sua conta")
    p_cross.add_argument("question", help="Pergunta transversal para todos os cadernos")
    p_cross.add_argument("--tags", help="Filtrar cadernos por tags (opcional)")

    # 2. Memória de Engenharia (ADRs e Bugs)
    p_adr = sub.add_parser("log-adr", help="Registra uma Decisão Arquitetural (ADR) na Base de Conhecimento")
    p_adr.add_argument("--title", required=True, help="Título da decisão técnica")
    p_adr.add_argument("--project", help="Nome do projeto")
    p_adr.add_argument("--context", required=True, help="Contexto e problema que motivou a decisão")
    p_adr.add_argument("--decision", required=True, help="Decisão técnica escolhida")
    p_adr.add_argument("--consequences", help="Consequências, benefícios e trade-offs")

    p_bug = sub.add_parser("log-bug", help="Registra um erro resolvido (Bug Postmortem) na Base de Conhecimento")
    p_bug.add_argument("--title", required=True, help="Título curto do bug/problema")
    p_bug.add_argument("--project", help="Nome do projeto")
    p_bug.add_argument("--symptom", required=True, help="Sintoma ou mensagem de erro exata")
    p_bug.add_argument("--cause", required=True, help="Causa-raiz diagnosticada")
    p_bug.add_argument("--solution", required=True, help="Solução definitiva aplicada")

    # 3. Auto-Catalogação e Índice Mestre
    sub.add_parser("sync-index", help="Atualiza o Índice Mestre da Base de Conhecimento no NotebookLM")

    # 4. Gerador Ativo de Estudo (Studio)
    p_kit = sub.add_parser(
        "study-kit",
        help="Gera materiais ativos de estudo (quiz, flashcards, mindmap, report, audio) no NotebookLM",
    )
    p_kit.add_argument(
        "--types",
        default="mindmap,quiz,flashcards",
        help="Tipos separados por vírgula: mindmap,quiz,flashcards,report,audio",
    )
    p_kit.add_argument("--topic", help="Foco ou tópico específico para o kit de estudo")

    # 5. Criação de Notebook e Sincronização de Chat/Código/Aprendizado
    p_new = sub.add_parser(
        "create-notebook",
        help="Cria um caderno NOVO no NotebookLM no final da conversa com chat, código e aprendizado",
    )
    p_new.add_argument("--title", required=True, help="Título do novo caderno no NotebookLM")
    p_new.add_argument("--alias", help="Alias opcional para o novo caderno")
    p_new.add_argument("--chat-file", help="Arquivo Markdown com o resumo/histórico da conversa")
    p_new.add_argument("--code-dir", help="Diretório do projeto para gerar documentação de código")
    p_new.add_argument("--project", help="Nome do projeto para a documentação de código")
    p_new.add_argument("--learning-file", help="Arquivo Markdown com a documentação de aprendizado")

    p_chat = sub.add_parser("sync-chat", help="Sincroniza o histórico/resumo da conversa para o Segundo Cérebro")
    p_chat.add_argument("--title", required=True, help="Título ou tema da conversa")
    p_chat.add_argument("--file", help="Caminho para arquivo Markdown com o registro da conversa")
    p_chat.add_argument("--text", help="Conteúdo em texto direto")

    p_code = sub.add_parser("sync-code", help="Gera e sincroniza a documentação de código de um projeto")
    p_code.add_argument("--dir", default=str(Path.cwd()), help="Diretório do projeto/repositório")
    p_code.add_argument("--project", help="Nome do projeto")

    p_doc = sub.add_parser("save-doc", help="Salva uma documentação de aprendizado ou nota estruturada")
    p_doc.add_argument("--title", required=True, help="Título do documento")
    p_doc.add_argument("--category", default="aprendizado", choices=["aprendizado", "codigo", "arquitetura", "chat"])
    p_doc.add_argument("--file", help="Caminho para arquivo Markdown/texto")
    p_doc.add_argument("--text", help="Conteúdo em texto direto")

    p_learn = sub.add_parser("sync-learning", help="Salva um guia de aprendizado no caderno")
    p_learn.add_argument("--topic", required=True, help="Tema do guia de aprendizado")
    p_learn.add_argument("--file", help="Caminho para arquivo Markdown/texto")
    p_learn.add_argument("--text", help="Conteúdo em texto direto")

    sub.add_parser("status", help="Lista todas as fontes do Segundo Cérebro")

    args = parser.parse_args()
    if args.command == "ask":
        cmd_ask(args)
    elif args.command == "cross-ask":
        cmd_cross_ask(args)
    elif args.command == "log-adr":
        cmd_log_adr(args)
    elif args.command == "log-bug":
        cmd_log_bug(args)
    elif args.command == "sync-index":
        cmd_sync_index(args)
    elif args.command == "study-kit":
        cmd_study_kit(args)
    elif args.command == "create-notebook":
        cmd_create_notebook(args)
    elif args.command == "sync-chat":
        cmd_sync_chat(args)
    elif args.command == "sync-code":
        cmd_sync_code(args)
    elif args.command == "save-doc":
        cmd_save_doc(args)
    elif args.command == "sync-learning":
        args.title = args.topic
        args.category = "aprendizado"
        cmd_save_doc(args)
    elif args.command == "status":
        cmd_status(args)


if __name__ == "__main__":
    main()
