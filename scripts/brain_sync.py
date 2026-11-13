#!/usr/bin/env python3
"""
Motor de Automação do "Segundo Cérebro de Engenharia & Aprendizado" (Antigravity -> NotebookLM).

Caderno Central (Alias: `cerebro`):
  ID: 4e930edb-9f8d-4a41-9987-52a3d1291720
  URL: https://notebook.google.com/notebook/4e930edb-9f8d-4a41-9987-52a3d1291720

Comandos:
  sync-chat --title T (--file F | --text TXT)  Sincroniza o resumo estruturado e histórico da conversa no Segundo Cérebro
  sync-code [--dir DIR] [--project NOME]       Gera a documentação técnica + mapa de funções/classes + código de um projeto e envia para o Segundo Cérebro
  save-doc --title T (--file F | --text TXT)   Salva/atualiza uma documentação de aprendizado ou arquitetura diretamente no Segundo Cérebro
  status                                       Lista todas as fontes indexadas no seu Segundo Cérebro no NotebookLM
"""

import argparse
import ast
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

BRAIN_NOTEBOOK_ID = "4e930edb-9f8d-4a41-9987-52a3d1291720"
BRAIN_NOTEBOOK_URL = f"https://notebook.google.com/notebook/{BRAIN_NOTEBOOK_ID}"
NLM_WRAPPER = Path("/home/antigravity/.gemini/nlm/nlm_wrapper.py")

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


def run_nlm(args: list[str]) -> str:
    cmd = [sys.executable, str(NLM_WRAPPER), "cli", *args]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"Erro ao executar nlm {' '.join(args)}:\n{res.stderr or res.stdout}"
        )
    return res.stdout.strip()


def list_sources(notebook_id: str) -> list[dict]:
    out = run_nlm(["source", "list", notebook_id, "--json"])
    if not out:
        return []
    data = json.loads(out)
    if isinstance(data, dict) and "sources" in data:
        return data["sources"]
    if isinstance(data, list):
        return data
    return []


def upsert_text_source(notebook_id: str, title: str, content: str) -> dict:
    """Adiciona ou atualiza uma fonte de texto no caderno (evitando duplicatas)."""
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
                run_nlm(["source", "delete", str(old_id), "--confirm"])
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
                symbols.append(f"- **Classe `{node.name}`**: {first_line}")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node) or ""
                first_line = doc.splitlines()[0] if doc else ""
                symbols.append(f"- **Função `{node.name}()`**: {first_line}")
    except Exception:
        pass
    return symbols


def build_code_documentation(target_dir: Path, project_name: str | None = None) -> tuple[str, str]:
    proj = project_name or target_dir.name
    doc_title = f"💻 Documentação de Código — {proj}"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {doc_title}",
        "",
        "Documentação técnica e estrutural gerada automaticamente pelo Antigravity para o Segundo Cérebro no NotebookLM.",
        "",
        f"- **Projeto:** `{proj}`",
        f"- **Caminho:** `{target_dir}`",
        f"- **Atualizado em:** {now_str}",
        "",
        "## 1. Árvore de Diretórios e Arquivos",
        "",
        "```text",
    ]

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
    lines.append("## 2. Mapa de Módulos, Funções e Classes")
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

    lines.append("## 3. Código-Fonte e Documentação dos Arquivos")
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
    upsert_text_source(args.notebook, full_title, content)
    print("✅ Conversa sincronizada com sucesso!")
    print(f"🔗 Caderno: {BRAIN_NOTEBOOK_URL}")


def cmd_sync_code(args: argparse.Namespace) -> None:
    target_dir = Path(args.dir).resolve()
    if not target_dir.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {target_dir}")
    doc_title, md_content = build_code_documentation(target_dir, project_name=args.project)
    print(f"💻 Sincronizando documentação de código '{doc_title}' para o Segundo Cérebro...")
    upsert_text_source(args.notebook, doc_title, md_content)
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
    upsert_text_source(args.notebook, full_title, content)
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
        run_nlm(["chat", "configure", nb_id, "--goal", "learning_guide"])
        run_nlm(["chat", "configure", nb_id, "--response-length", "longer"])
    except Exception:
        pass

    if args.alias:
        try:
            run_nlm(["alias", "set", args.alias, nb_id])
        except Exception:
            pass

    if args.chat_file:
        chat_content = Path(args.chat_file).read_text(encoding="utf-8")
        upsert_text_source(nb_id, f"💬 Chat & Decisões — {title}", chat_content)
        print("  ✓ Fonte de Chat & Decisões adicionada!")

    if args.code_dir:
        target_dir = Path(args.code_dir).resolve()
        doc_title, md_content = build_code_documentation(target_dir, project_name=args.project or title)
        upsert_text_source(nb_id, doc_title, md_content)
        print("  ✓ Fonte de Documentação de Código adicionada!")

    if args.learning_file:
        learn_content = Path(args.learning_file).read_text(encoding="utf-8")
        upsert_text_source(nb_id, f"📘 Aprendizado — {title}", learn_content)
        print("  ✓ Fonte de Guia de Aprendizado adicionada!")

    print(f"\n🎉 Novo Notebook pronto: {nb_url}")


def cmd_status(args: argparse.Namespace) -> None:
    nb_url = (
        BRAIN_NOTEBOOK_URL
        if args.notebook in (BRAIN_NOTEBOOK_ID, "cerebro")
        else f"https://notebook.google.com/notebook/{args.notebook}"
    )
    print("=" * 72)
    print("🧠 SEGUNDO CÉREBRO — ENGENHARIA & APRENDIZADO (NOTEBOOKLM)")
    print(f"🔗 Link: {nb_url}")
    print("=" * 72)
    out = run_nlm(["source", "list", args.notebook])
    print(out)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automação do Segundo Cérebro de Engenharia & Aprendizado (Antigravity -> NotebookLM)"
    )
    parser.add_argument(
        "--notebook",
        default=BRAIN_NOTEBOOK_ID,
        help="ID ou alias do caderno no NotebookLM (padrão: cerebro)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

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
    if args.command == "create-notebook":
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
