#!/usr/bin/env python3
"""
Wrapper persistente para o Gemini Notebook MCP & CLI (notebooklm-mcp-cli) no Antigravity.

Resolve automaticamente 4 limitações do ambiente de VMs efêmeras do Antigravity:
1. Corrige NO_PROXY (`[::1]`) que causa `httpx.InvalidURL: Invalid port: ':1]'`.
2. Auto-instala `notebooklm-mcp-cli` via `uv tool install` se a VM for nova (enviando logs para stderr para não quebrar o JSON-RPC do MCP).
3. Sincroniza as credenciais salvas em `/home/antigravity/.gemini/nlm/storage` (persistente entre conversas) com `~/.notebooklm-mcp-cli` (disco local com suporte a chmod 0700/0600).
4. Permite executar tanto o servidor MCP (`nlm_wrapper.py mcp`) quanto a CLI (`nlm_wrapper.py cli <args>`).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PERSISTENT_DIR = Path("/home/antigravity/.gemini/nlm/storage")
LOCAL_STORAGE_DIR = Path.home() / ".notebooklm-mcp-cli"
UV_BIN = Path("/usr/local/bin/uv")
LOCAL_BIN = Path.home() / ".local" / "bin"


def sanitize_no_proxy(env: dict[str, str]) -> None:
    for var in ("NO_PROXY", "no_proxy"):
        val = env.get(var)
        if val:
            parts = [p.strip() for p in val.split(",") if p.strip() != "[::1]"]
            env[var] = ",".join(parts)


def ensure_installed(env: dict[str, str]) -> None:
    nlm_bin = LOCAL_BIN / "nlm"
    mcp_bin = LOCAL_BIN / "notebooklm-mcp"
    if nlm_bin.exists() and mcp_bin.exists():
        return
    subprocess.run(
        [str(UV_BIN), "tool", "install", "notebooklm-mcp-cli"],
        stdout=sys.stderr,
        stderr=sys.stderr,
        env=env,
        check=True,
    )


def sync_from_persistent() -> None:
    if not PERSISTENT_DIR.exists():
        return
    LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        LOCAL_STORAGE_DIR.chmod(0o700)
    except OSError:
        pass

    for root, dirs, files in os.walk(PERSISTENT_DIR):
        rel = Path(root).relative_to(PERSISTENT_DIR)
        target_root = LOCAL_STORAGE_DIR / rel
        target_root.mkdir(parents=True, exist_ok=True)
        try:
            target_root.chmod(0o700)
        except OSError:
            pass
        for d in dirs:
            td = target_root / d
            td.mkdir(parents=True, exist_ok=True)
            try:
                td.chmod(0o700)
            except OSError:
                pass
        for f in files:
            src_file = Path(root) / f
            dst_file = target_root / f
            if not dst_file.exists() or src_file.stat().st_mtime >= dst_file.stat().st_mtime:
                shutil.copyfile(src_file, dst_file)
                try:
                    dst_file.chmod(0o600)
                except OSError:
                    pass


def sync_to_persistent() -> None:
    if not LOCAL_STORAGE_DIR.exists():
        return
    PERSISTENT_DIR.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(LOCAL_STORAGE_DIR):
        rel = Path(root).relative_to(LOCAL_STORAGE_DIR)
        if "chrome-profile" in rel.parts or "backups" in rel.parts:
            continue
        target_root = PERSISTENT_DIR / rel
        target_root.mkdir(parents=True, exist_ok=True)
        for d in dirs:
            if d in ("chrome-profile", "backups"):
                continue
            (target_root / d).mkdir(parents=True, exist_ok=True)
        for f in files:
            if f.endswith(".lock") or ".tmp." in f:
                continue
            src_file = Path(root) / f
            dst_file = target_root / f
            shutil.copyfile(src_file, dst_file)


def main() -> int:
    env = os.environ.copy()
    sanitize_no_proxy(env)
    ensure_installed(env)
    sync_from_persistent()

    args = sys.argv[1:]
    mode = "mcp"
    if args and args[0] in ("mcp", "cli"):
        mode = args[0]
        args = args[1:]

    env["PATH"] = f"{LOCAL_BIN}:{env.get('PATH', '')}"
    env.setdefault("NLM_AUTH_STORAGE", "file")
    env.setdefault("NOTEBOOKLM_HL", "pt-BR")

    target_bin = LOCAL_BIN / ("notebooklm-mcp" if mode == "mcp" else "nlm")
    try:
        proc = subprocess.run([str(target_bin), *args], env=env)
        return proc.returncode
    finally:
        sync_to_persistent()


if __name__ == "__main__":
    raise SystemExit(main())
