#!/usr/bin/env python3
"""
Ponte de Automação Antigravity <-> Google Drive / Docs <-> NotebookLM.

Comandos:
  status                         Lista os documentos nas pastas de Fontes e Exportados no Drive
  push <arquivo.md> [--title T]  Envia ou atualiza um arquivo Markdown como Google Doc na pasta 01_Fontes_para_NotebookLM
  pull <id_ou_nome> [--out ARQ]  Exporta um Google Doc da pasta 02_Exportados_do_NotebookLM para Markdown local
  bundle-repo [--dir DIR]        Empacota a estrutura e arquivos principais de um repositório e envia como Google Doc para o NotebookLM
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "notebooklm_manifest.json"

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

TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    ".html",
    ".css",
}


def run_cmd(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Erro ao executar {' '.join(cmd)}:\n{result.stderr or result.stdout}"
        )
    return result.stdout.strip()


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifesto não encontrado em {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(data: dict) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def list_drive_folder(folder_id: str) -> list[dict]:
    out = run_cmd(["gdrive", "readonly", "ls", folder_id, "--json"])
    if not out:
        return []
    return json.loads(out)


def format_doc_url(item: dict) -> str:
    file_id = item["id"]
    mime = item.get("mimeType", "")
    if "document" in mime:
        return f"https://docs.google.com/document/d/{file_id}/edit"
    return f"https://drive.google.com/file/d/{file_id}/view"


def cmd_status(_args: argparse.Namespace) -> None:
    manifest = load_manifest()
    folders = manifest["drive_folders"]

    print("=" * 72)
    print(f"Pasta Principal: {folders['root']['name']}")
    print(f"Link: {folders['root']['url']}")
    print("=" * 72)

    for key, label in [
        ("sources_for_notebooklm", "01_Fontes_para_NotebookLM (Antigravity -> NotebookLM)"),
        ("exports_from_notebooklm", "02_Exportados_do_NotebookLM (NotebookLM -> Antigravity)"),
    ]:
        f_info = folders[key]
        print(f"\n📂 {label}")
        print(f"   URL da Pasta: {f_info['url']}")
        items = list_drive_folder(f_info["id"])
        if not items:
            print("   (vazia)")
        else:
            for item in items:
                url = format_doc_url(item)
                mod = item.get("modifiedTime", "")[:19].replace("T", " ")
                print(f"   • {item['name']} (Modificado: {mod})")
                print(f"     {url}")


def push_markdown_to_drive(
    md_path: Path, title: str | None = None, manifest_key: str | None = None
) -> dict:
    if not md_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {md_path}")

    manifest = load_manifest()
    sources_folder_id = manifest["drive_folders"]["sources_for_notebooklm"]["id"]
    synced = manifest.setdefault("synced_documents", {})

    key = manifest_key or str(md_path.resolve().relative_to(REPO_ROOT)) if md_path.resolve().is_relative_to(REPO_ROOT) else md_path.stem
    doc_title = title or md_path.stem.replace("_", " ").replace("-", " ").title()

    existing = synced.get(key)
    if existing and existing.get("doc_id"):
        doc_id = existing["doc_id"]
        print(f"🔄 Atualizando Google Doc existente: '{existing['title']}'...")
        run_cmd(
            [
                "gdocs",
                "mutate",
                "import-md",
                str(md_path),
                "--update",
                doc_id,
                "--auto-fit-tables",
            ]
        )
        if title and title != existing.get("title"):
            run_cmd(["gdrive", "mutate", "rename", doc_id, doc_title])
            existing["title"] = doc_title
        save_manifest(manifest)
        print(f"✅ Atualizado com sucesso! Link: {existing['url']}")
        return existing

    print(f"🚀 Criando novo Google Doc '{doc_title}' em 01_Fontes_para_NotebookLM...")
    out = run_cmd(
        [
            "gdocs",
            "mutate",
            "import-md",
            str(md_path),
            "--title",
            doc_title,
            "--auto-fit-tables",
        ]
    )
    match = re.search(r"ID:\s*([a-zA-Z0-9_-]+)", out)
    if not match:
        link_match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", out)
        if not link_match:
            raise RuntimeError(f"Não foi possível extrair o ID do documento de:\n{out}")
        doc_id = link_match.group(1)
    else:
        doc_id = match.group(1)

    run_cmd(["gdrive", "mutate", "mv", doc_id, sources_folder_id])
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    entry = {
        "title": doc_title,
        "doc_id": doc_id,
        "url": doc_url,
        "local_path": str(md_path),
        "folder": "sources_for_notebooklm",
    }
    synced[key] = entry
    save_manifest(manifest)
    print(f"✅ Criado e movido para 01_Fontes_para_NotebookLM!")
    print(f"🔗 Link: {doc_url}")
    return entry


def cmd_push(args: argparse.Namespace) -> None:
    md_path = Path(args.file).resolve()
    push_markdown_to_drive(md_path, title=args.title, manifest_key=args.key)


def cmd_pull(args: argparse.Namespace) -> None:
    manifest = load_manifest()
    exports_folder_id = manifest["drive_folders"]["exports_from_notebooklm"]["id"]
    sources_folder_id = manifest["drive_folders"]["sources_for_notebooklm"]["id"]

    target = args.target
    doc_id = None
    doc_name = target

    if re.fullmatch(r"[a-zA-Z0-9_-]{25,}", target):
        doc_id = target
    else:
        items = list_drive_folder(exports_folder_id) + list_drive_folder(sources_folder_id)
        for item in items:
            if target.lower() in item["name"].lower():
                doc_id = item["id"]
                doc_name = item["name"]
                break

    if not doc_id:
        raise RuntimeError(
            f"Nenhum documento encontrado com nome ou ID '{target}' nas pastas do NotebookLM."
        )

    notes_dir = REPO_ROOT / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", doc_name.lower()).strip("_")
    out_path = Path(args.out).resolve() if args.out else (notes_dir / f"{safe_name}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📥 Exportando '{doc_name}' para {out_path}...")
    run_cmd(
        [
            "gdocs",
            "readonly",
            "export",
            doc_id,
            "--format",
            "md",
            "--output",
            str(out_path),
        ]
    )
    print(f"✅ Arquivo salvo em: {out_path}")


def cmd_bundle_repo(args: argparse.Namespace) -> None:
    target_dir = Path(args.dir).resolve()
    if not target_dir.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {target_dir}")

    repo_name = target_dir.name
    doc_title = args.title or f"Fonte NotebookLM — Repositório {repo_name}"

    lines = [
        f"# {doc_title}",
        "",
        f"Resumo consolidado do repositório `{repo_name}` gerado automaticamente pelo Antigravity para indexação no Google NotebookLM.",
        "",
        "## 1. Estrutura de Arquivos",
        "",
        "```text",
    ]

    collected_files: list[Path] = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
        rel_root = Path(root).relative_to(target_dir)
        depth = 0 if str(rel_root) == "." else len(rel_root.parts)
        indent = "  " * depth
        if str(rel_root) != ".":
            lines.append(f"{indent}{rel_root.name}/")
        for f in sorted(files):
            file_path = Path(root) / f
            lines.append(f"{indent}  {f}")
            if file_path.suffix.lower() in TEXT_EXTENSIONS and file_path.stat().st_size < 60_000:
                collected_files.append(file_path)

    lines.append("```")
    lines.append("")
    lines.append("## 2. Conteúdo dos Arquivos do Projeto")
    lines.append("")

    for file_path in collected_files:
        rel = str(file_path.relative_to(target_dir)).replace("_", r"\_")
        ext = file_path.suffix.lstrip(".") or "text"
        content = file_path.read_text(encoding="utf-8", errors="replace")
        lines.append(f"### Arquivo: `{rel}`")
        lines.append("")
        lines.append(f"```{ext}")
        lines.append(content.rstrip())
        lines.append("```")
        lines.append("")

    bundle_path = Path("/tmp") / f"bundle_{repo_name}.md"
    bundle_path.write_text("\n".join(lines), encoding="utf-8")

    push_markdown_to_drive(
        bundle_path,
        title=doc_title,
        manifest_key=f"bundle:{repo_name}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ponte de Automação Antigravity <-> Google Drive/Docs <-> NotebookLM"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Lista os arquivos nas pastas do NotebookLM no Drive")

    p_push = sub.add_parser(
        "push", help="Envia ou atualiza um arquivo Markdown como Google Doc para o NotebookLM"
    )
    p_push.add_argument("file", help="Caminho do arquivo Markdown local")
    p_push.add_argument("--title", help="Título do Google Doc no Drive")
    p_push.add_argument("--key", help="Chave personalizada no manifesto")

    p_pull = sub.add_parser(
        "pull", help="Baixa um Google Doc exportado do NotebookLM para Markdown local"
    )
    p_pull.add_argument("target", help="Nome (ou parte do nome) ou ID do Google Doc")
    p_pull.add_argument("--out", help="Caminho de saída local (.md)")

    p_bundle = sub.add_parser(
        "bundle-repo",
        help="Empacota o repositório em um Google Doc pronto para o NotebookLM",
    )
    p_bundle.add_argument("--dir", default=str(REPO_ROOT), help="Diretório do repositório")
    p_bundle.add_argument("--title", help="Título do Google Doc gerado")

    args = parser.parse_args()
    if args.command == "status":
        cmd_status(args)
    elif args.command == "push":
        cmd_push(args)
    elif args.command == "pull":
        cmd_pull(args)
    elif args.command == "bundle-repo":
        cmd_bundle_repo(args)


if __name__ == "__main__":
    main()
