# 🧠 Conectar Antigravity com NotebookLM via MCP — Base de Conhecimento Inteligente v2.0 (`brain_sync.py`)

Sistema completo de **Base de Conhecimento Inteligente de Engenharia & Aprendizado** que conecta o **Google Antigravity** ao **Google NotebookLM (Gemini Notebook)** de forma **bidirecional, auto-catalogada e proativa**.

🔗 **Caderno Central no NotebookLM:** [`Conectar Antigravity com NotebookLM via MCP`](https://notebook.google.com/notebook/4e930edb-9f8d-4a41-9987-52a3d1291720)
- **Notebook ID:** `4e930edb-9f8d-4a41-9987-52a3d1291720` (Alias: `cerebro`)
- **Modo de IA do Caderno:** `learning_guide` (Guia de Aprendizado com respostas detalhadas)

---

## 🌟 Os 4 Pilares da Base de Conhecimento Inteligente

### 1. 🔍 Consulta Inteligente / Memória Bidirecional (`ask` & `cross-ask`)
Em vez de apenas enviar arquivos para o NotebookLM, o Antigravity **consulta sua base de conhecimento antes de codar ou depurar** para reaproveitar suas decisões, arquitetura e soluções anteriores:
- `ask`: Faz perguntas diretamente ao seu Segundo Cérebro.
- `cross-ask`: Faz uma busca transversal simultânea em **todos os cadernos** da sua conta do NotebookLM, trazendo citações por caderno.

### 2. 🏛️ Memória de Engenharia (`log-adr` & `log-bug`)
Mantém dois livros vivos dentro do seu Segundo Cérebro (e espelhados em `/home/antigravity/.gemini/nlm/knowledge/`):
- **`🏛️ Memória de Arquitetura — Decisões Técnicas (ADRs)` (`log-adr`)**: Registra decisões arquiteturais no padrão de engenharia (Contexto $\rightarrow$ Decisão $\rightarrow$ Consequências/Trade-offs).
- **`🛠️ Catálogo de Soluções de Bugs & Troubleshooting` (`log-bug`)**: Registra erros complexos resolvidos (Sintoma $\rightarrow$ Causa-Raiz $\rightarrow$ Solução Definitiva) para você nunca mais perder tempo com o mesmo bug.

### 3. 🗂️ Auto-Catalogação, Auto-Tagging & Índice Mestre (`sync-index`)
- Cada fonte enviada passa por **detecção automática de tags** (`#python`, `#javascript`, `#frontend`, `#backend`, `#mcp`, `#arquitetura`, `#bugfix`, `#automacao`, `#ia`).
- Mantém o catálogo local `/home/antigravity/.gemini/nlm/knowledge/catalog.json` e atualiza a fonte **`🗂️ Índice Mestre — Catálogo da Base de Conhecimento`** dentro do NotebookLM com o mapa de todos os seus cadernos, fontes e tags.
- O gerador `sync-code` extrai automaticamente dependências (`package.json`, `requirements.txt`, `pyproject.toml`, `mcp_config.json`), árvore de arquivos, assinaturas AST (`class`, `def`, parâmetros e métodos) e código-fonte.

### 4. 🎓 Gerador Ativo de Kit de Estudos (`study-kit`)
Com um único comando, aciona o Studio do NotebookLM para criar materiais de fixação a partir do que você programou ou estudou:
- **Mapa Mental (`mindmap`)**, **Quiz Interativo (`quiz`)**, **Flashcards (`flashcards`)**, **Guia de Estudos (`report`)** e **Podcast em Português (`audio`)**.

---

## 💬 Como Chamar a Skill pelo Nome **"Lucas"** (em Qualquer Conversa)

A skill está registrada no Antigravity com o nome **`lucas`** ([`.agents/skills/lucas/SKILL.md`](./.agents/skills/lucas/SKILL.md)). Em qualquer conversa, basta chamar por **"Lucas"**:

- **Criar um Notebook novo no final da conversa:**
  > *"Lucas, crie um notebook com o nome 'Projeto X' com o resumo deste chat, a documentação do código e um guia de aprendizado."*
- **Alimentar a Base de Conhecimento Central (`Conectar Antigravity com NotebookLM via MCP`):**
  > *"Lucas, sincronize esta conversa, o código, o aprendizado e atualize o Índice Mestre na minha Base de Conhecimento."*
- **Consultar sua base antes de programar:**
  > *"Lucas, consulte minha Base de Conhecimento sobre quais decisões arquiteturais e soluções de bugs já registramos."*
- **Registrar uma decisão ou bug resolvido:**
  > *"Lucas, registre esta decisão como um ADR e salve a solução deste bug na minha Base de Conhecimento."*
- **Gerar um Kit de Estudos:**
  > *"Lucas, gere um Kit de Estudos (Mapa Mental, Quiz e Flashcards) sobre o que implementamos hoje."*

---

## 🛠️ Referência Rápida de Comandos (`brain_sync.py`)

```bash
# 1. Consultar o Segundo Cérebro (RAG Bidirecional)
python3 /home/antigravity/.gemini/nlm/brain_sync.py ask "Quais bugs já resolvemos e quais decisões de arquitetura tomamos?"

# 2. Consultar TODOS os cadernos da conta ao mesmo tempo
python3 /home/antigravity/.gemini/nlm/brain_sync.py cross-ask "Resumo de todos os projetos documentados"

# 3. Registrar uma Decisão de Arquitetura (ADR)
python3 /home/antigravity/.gemini/nlm/brain_sync.py log-adr \
  --title "Integração Direta via MCP em vez de Ponte Google Drive" \
  --project "Antigravity-e-NotebookLM" \
  --context "A ponte via Google Drive exigia vinculação manual no NotebookLM" \
  --decision "Adotar o servidor MCP oficial (notebooklm-mcp-cli) com wrapper persistente" \
  --consequences "Sincronização 100% automática, bidirecional e sem etapas manuais"

# 4. Registrar uma Solução de Bug (Postmortem)
python3 /home/antigravity/.gemini/nlm/brain_sync.py log-bug \
  --title "Falha chmod Operation not permitted em /shared/user/.gemini" \
  --project "Antigravity-e-NotebookLM" \
  --symptom "PermissionError: [Errno 1] Operation not permitted ao salvar perfil no FUSE" \
  --cause "O diretório persistente ~/.gemini é montado via FUSE e bloqueia chamadas chmod" \
  --solution "Sincronizar credenciais entre ~/.gemini/nlm/storage e o disco local ~/.notebooklm-mcp-cli via nlm_wrapper.py"

# 5. Atualizar o Índice Mestre da Base de Conhecimento
python3 /home/antigravity/.gemini/nlm/brain_sync.py sync-index

# 6. Gerar Kit de Estudos no NotebookLM Studio (Mapa Mental, Quiz, Flashcards, Podcast)
python3 /home/antigravity/.gemini/nlm/brain_sync.py study-kit \
  --types mindmap,quiz,flashcards \
  --topic "Arquitetura MCP e Base de Conhecimento Inteligente"

# 7. Sincronizar Chat, Código ou Guia de Aprendizado
python3 /home/antigravity/.gemini/nlm/brain_sync.py sync-chat --title "Tema" --file /tmp/resumo.md
python3 /home/antigravity/.gemini/nlm/brain_sync.py sync-code --dir /caminho/do/projeto --project "Nome"
python3 /home/antigravity/.gemini/nlm/brain_sync.py sync-learning --topic "Tema" --file /tmp/aprendizado.md

# 8. Criar um Notebook NOVO exclusivo no final da conversa
python3 /home/antigravity/.gemini/nlm/brain_sync.py create-notebook \
  --title "Nome do Novo Caderno" \
  --chat-file /tmp/resumo.md \
  --code-dir /caminho/do/projeto \
  --learning-file /tmp/aprendizado.md
```
