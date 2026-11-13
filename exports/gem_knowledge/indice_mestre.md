# 🗂️ Índice Mestre — Catálogo da Base de Conhecimento Inteligente

- **Exportado em:** 2026-11-13 11:11 (última atualização do catálogo: `2026-11-13 18:58 UTC`)
- **Caderno Central (Segundo Cérebro):** `Conectar Antigravity com NotebookLM via MCP` (`4e930edb-9f8d-4a41-9987-52a3d1291720`) — https://notebook.google.com/notebook/4e930edb-9f8d-4a41-9987-52a3d1291720

## 1. Cadernos Mapeados no Catálogo

- **Conectar Antigravity com NotebookLM via MCP** — ID: `4e930edb-9f8d-4a41-9987-52a3d1291720` (https://notebook.google.com/notebook/4e930edb-9f8d-4a41-9987-52a3d1291720)
- **Rotinas & Finanças** — ID: `c8287e6e-1f69-42cf-89b2-576c18b594c4` (https://notebook.google.com/notebook/c8287e6e-1f69-42cf-89b2-576c18b594c4)
- **Teste Marina** — ID: `6b65527c-675e-465d-a0bf-e6482b98f566` (https://notebook.google.com/notebook/6b65527c-675e-465d-a0bf-e6482b98f566)

## 2. Histórico de Entradas Catalogadas & Tags

- **[2026-11-13 18:58] 🗂️ Índice Mestre — Catálogo da Base de Conhecimento** (`indice`) — Tags: `#arquitetura`, `#automacao`, `#backend`, `#bugfix`, `#frontend`, `#ia`, `#indice`, `#javascript`, `#mcp`, `#python`
  - Resumo: Mapa global de todos os cadernos, fontes, ADRs, bugs resolvidos e tags da Base de Conhecimento.
- **[2026-11-13 18:57] 💻 Documentação de Código — Rotinas & Finanças** (`codigo`) — Tags: `#arquitetura`, `#automacao`, `#backend`, `#bugfix`, `#codigo`, `#frontend`, `#ia`, `#javascript`, `#python`
  - Resumo: Documentação completa de código e AST do projeto Rotinas & Finanças.
- **[2026-11-13 18:56] 💬 Chat & Decisões — Rotinas e Finanças - Dashboard Pessoal** (`chat`) — Tags: `#arquitetura`, `#automacao`, `#chat`, `#frontend`, `#ia`, `#javascript`, `#python`
  - Resumo: Resumo do Projeto: Rotinas & Finanças Pessoais.
- **[2026-11-13 18:45] 💻 Documentação de Código — Antigravity-e-NotebookLM** (`codigo`) — Tags: `#arquitetura`, `#automacao`, `#backend`, `#bugfix`, `#codigo`, `#frontend`, `#ia`, `#javascript`, `#mcp`, `#python`
  - Resumo: Documentação completa de código e AST do projeto Antigravity-e-NotebookLM.
- **[2026-11-13 18:44] 🏛️ Memória de Arquitetura — Decisões Técnicas (ADRs)** (`arquitetura`) — Tags: `#arquitetura`, `#automacao`, `#backend`, `#frontend`, `#ia`, `#mcp`
  - Resumo: ADR (Antigravity-e-NotebookLM): Arquitetura Híbrida: Skill Global + Subagente Autônomo Lucas -> Combinar a Skill global `lucas` (`.agents/skills/lucas/SKILL.md`) com o Subagente Autônomo `lucas` (`.agents/agents/lucas.md` via `define_subagent` e `invoke_subagent`).
- **[2026-11-13 18:13] 🛠️ Catálogo de Soluções de Bugs & Troubleshooting** (`bugfix`) — Tags: `#arquitetura`, `#automacao`, `#bugfix`, `#frontend`, `#ia`, `#mcp`, `#python`
  - Resumo: Bug (Antigravity-e-NotebookLM): PermissionError `chmod` em `/shared/user/.gemini` e `InvalidURL [::1]` no `httpx` -> Solução: Criar `nlm_wrapper.py` que sincroniza credenciais entre `~/.gemini/nlm/storage` e `~/.notebooklm-mcp-cli` (disco local) e remove `[::1]` de `NO_PROXY` antes de invocar o `nlm`.
