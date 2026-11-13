# 🛠️ Catálogo de Soluções de Bugs & Troubleshooting

Base de conhecimento de erros técnicos encontrados, causas-raiz diagnosticadas e soluções definitivas.

---

## 🐛 Bug / Problema: PermissionError chmod em /shared/user/.gemini e InvalidURL [::1] no httpx
- **Data:** 2026-11-13 18:13
- **Projeto:** `Antigravity-e-NotebookLM`
- **Sintoma / Erro Exato:** 1) PermissionError: [Errno 1] Operation not permitted ao salvar perfil no diretório FUSE ~/.gemini; 2) httpx.InvalidURL: Invalid port: ':1]' ao autenticar.
- **Causa-Raiz:** 1) O mount FUSE de /shared/user/.gemini bloqueia chamadas chmod; 2) A variável NO_PROXY da VM inclui [::1], que quebra o parser do httpx.
- **Solução Definitiva:** Criar nlm_wrapper.py que sincroniza credenciais entre ~/.gemini/nlm/storage e ~/.notebooklm-mcp-cli (disco local) e remove [::1] de NO_PROXY antes de invocar o nlm.

---

