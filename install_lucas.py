#!/usr/bin/env python3
"""
Instalador Multiplataforma (Windows & Linux) do Agente Lucas e da Skill `lucas` no Antigravity.

Instala em `C:\\Users\\<usuario>\\.gemini` (Windows) ou `~/.gemini` (Linux/macOS):
  1. `~/.gemini/nlm/nlm_wrapper.py` e `~/.gemini/nlm/brain_sync.py`
  2. `~/.gemini/nlm/lucas_agent.md`
  3. Skill `lucas` em `~/.gemini/antigravity/skills/lucas` e `~/.gemini/skills/lucas`
  4. Configuração do servidor MCP `gemini-notebook-mcp` em `~/.gemini/antigravity/mcp_config.json`
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
GEMINI_DIR = Path.home() / ".gemini"
NLM_DIR = GEMINI_DIR / "nlm"


def copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_tree(item, target)
        else:
            shutil.copyfile(item, target)


def configure_mcp(config_path: Path, wrapper_path: Path) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    if not isinstance(data.get("mcpServers"), dict):
        data["mcpServers"] = {}

    data["mcpServers"]["gemini-notebook-mcp"] = {
        "command": sys.executable,
        "args": [str(wrapper_path), "mcp"],
        "env": {
            "NLM_AUTH_STORAGE": "file",
            "NOTEBOOKLM_HL": "pt-BR",
        },
    }
    config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    print(f"🚀 Instalando o Agente Lucas e a Base de Conhecimento Inteligente em: {GEMINI_DIR}")
    NLM_DIR.mkdir(parents=True, exist_ok=True)
    (NLM_DIR / "knowledge").mkdir(parents=True, exist_ok=True)
    (NLM_DIR / "storage").mkdir(parents=True, exist_ok=True)

    # 1. Copiar scripts principais
    for script_name in ("nlm_wrapper.py", "brain_sync.py"):
        src = REPO_ROOT / "scripts" / script_name
        dst = NLM_DIR / script_name
        shutil.copyfile(src, dst)
        print(f"  ✓ Script instalado: {dst}")

    # 2. Copiar definição do Agente Lucas
    agent_src = REPO_ROOT / ".agents" / "agents" / "lucas.md"
    if agent_src.exists():
        agent_dst = NLM_DIR / "lucas_agent.md"
        shutil.copyfile(agent_src, agent_dst)
        print(f"  ✓ Definição do Agente Lucas instalada: {agent_dst}")

    # 3. Instalar a Skill 'lucas' nos diretórios globais do Antigravity
    skill_src = REPO_ROOT / ".agents" / "skills" / "lucas"
    for skill_dst in (
        GEMINI_DIR / "antigravity" / "skills" / "lucas",
        GEMINI_DIR / "skills" / "lucas",
    ):
        copy_tree(skill_src, skill_dst)
        print(f"  ✓ Skill 'lucas' instalada em: {skill_dst}")

    # 4. Configurar o servidor MCP
    wrapper_path = NLM_DIR / "nlm_wrapper.py"
    for mcp_cfg in (
        GEMINI_DIR / "antigravity" / "mcp_config.json",
        GEMINI_DIR / "config" / "mcp_config.json",
    ):
        configure_mcp(mcp_cfg, wrapper_path)
        print(f"  ✓ Servidor MCP configurado em: {mcp_cfg}")

    print("\n📦 Verificando instalação do pacote 'notebooklm-mcp-cli'...")
    try:
        subprocess.run(
            [sys.executable, str(wrapper_path), "cli", "--version"],
            check=False,
        )
    except Exception as e:
        print(f"  ⚠️ Aviso ao verificar CLI: {e}")

    print("\n✅ Agente Lucas instalado com sucesso!")
    print(f"👉 No Windows/Linux, você pode usar: python \"{NLM_DIR / 'brain_sync.py'}\" status")


if __name__ == "__main__":
    main()
