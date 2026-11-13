#!/usr/bin/env python3
"""
Wrapper multiplataforma (Linux Cloud VM & Windows Desktop) para o Gemini Notebook MCP & CLI (notebooklm-mcp-cli) no Antigravity.

Resolve automaticamente as particularidades de ambos os ambientes:
1. Corrige NO_PROXY (`[::1]`) que causa `httpx.InvalidURL: Invalid port: ':1]'`.
2. Auto-instala `notebooklm-mcp-cli` via `uv tool install` ou `pip install` se ainda não estiver instalado.
3. Sincroniza as credenciais salvas em `~/.gemini/nlm/storage` com `~/.notebooklm-mcp-cli`.
4. Permite executar tanto o servidor MCP (`nlm_wrapper.py mcp`) quanto a CLI (`nlm_wrapper.py cli <args>`).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PERSISTENT_DIR = Path.home() / ".gemini" / "nlm" / "storage"
LOCAL_STORAGE_DIR = Path.home() / ".notebooklm-mcp-cli"
IS_WINDOWS = os.name == "nt"
LOCAL_BIN = (
    Path(os.environ.get("APPDATA", str(Path.home()))) / "Python" / "Scripts"
    if IS_WINDOWS
    else Path.home() / ".local" / "bin"
)


def sanitize_no_proxy(env: dict[str, str]) -> None:
    for var in ("NO_PROXY", "no_proxy"):
        val = env.get(var)
        if val:
            parts = [p.strip() for p in val.split(",") if p.strip() != "[::1]"]
            env[var] = ",".join(parts)


def find_executable(name: str) -> str | None:
    exe_name = f"{name}.exe" if IS_WINDOWS else name
    candidates = [
        LOCAL_BIN / exe_name,
        Path.home() / ".local" / "bin" / exe_name,
        Path(sys.executable).parent / exe_name,
        Path(sys.executable).parent / "Scripts" / exe_name,
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return shutil.which(name)


def ensure_installed(env: dict[str, str]) -> None:
    if find_executable("nlm") and find_executable("notebooklm-mcp"):
        return
    uv_bin = shutil.which("uv") or (
        "/usr/local/bin/uv" if Path("/usr/local/bin/uv").exists() else None
    )
    if uv_bin:
        subprocess.run(
            [uv_bin, "tool", "install", "notebooklm-mcp-cli"],
            stdout=sys.stderr,
            stderr=sys.stderr,
            env=env,
            check=False,
        )
    if not find_executable("nlm"):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "notebooklm-mcp-cli"],
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

    sep = ";" if IS_WINDOWS else ":"
    env["PATH"] = f"{LOCAL_BIN}{sep}{Path.home() / '.local' / 'bin'}{sep}{env.get('PATH', '')}"
    env.setdefault("NLM_AUTH_STORAGE", "file")
    env.setdefault("NOTEBOOKLM_HL", "pt-BR")

    bin_name = "notebooklm-mcp" if mode == "mcp" else "nlm"
    target_bin = find_executable(bin_name) or bin_name
    try:
        res = subprocess.run([target_bin, *args], env=env)
        return res.returncode
    finally:
        sync_to_persistent()


if __name__ == "__main__":
    raise SystemExit(main())
