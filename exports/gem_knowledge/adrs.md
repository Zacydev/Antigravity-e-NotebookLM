# 🏛️ Memória de Arquitetura — Registro de Decisões Técnicas (ADRs)

Este documento consolida todas as decisões arquiteturais importantes tomadas nos projetos no Antigravity.

---

## ADR: Integração Direta via MCP em vez de Ponte Google Drive
- **Data:** 2026-11-13 18:13
- **Projeto:** `Antigravity-e-NotebookLM`
- **Status:** Aceito / Implementado
- **Contexto / Problema:** A ponte via Google Drive exigia vinculação manual de documentos no NotebookLM e não permitia consultas bidirecionais (RAG) nem geração ativa de artefatos no Studio.
- **Decisão Tomada:** Adotar o servidor MCP oficial (notebooklm-mcp-cli) com wrapper de persistência nlm_wrapper.py e orquestrador brain_sync.py v2.0.
- **Consequências e Trade-offs:** Sincronização 100% automática, consultas RAG bidirecionais (ask/cross-ask), auto-catalogação e geração de Kits de Estudo via CLI/MCP.

---

## ADR: Arquitetura Híbrida: Skill Global + Subagente Autônomo Lucas
- **Data:** 2026-11-13 18:44
- **Projeto:** `Antigravity-e-NotebookLM`
- **Status:** Aceito / Implementado
- **Contexto / Problema:** Necessidade de executar tarefas de documentação, RAG e sincronização com o NotebookLM sem poluir ou consumir a janela de contexto da conversa principal.
- **Decisão Tomada:** Combinar a Skill global 'lucas' (.agents/skills/lucas/SKILL.md) com o Subagente Autônomo 'lucas' (.agents/agents/lucas.md via define_subagent e invoke_subagent).
- **Consequências e Trade-offs:** O Agente Lucas opera em segundo plano com contexto isolado e ferramentas completas de leitura/escrita/MCP, devolvendo apenas o relatório consolidado ao chat principal.

---

