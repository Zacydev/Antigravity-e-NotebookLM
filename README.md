# 🧠 Antigravity + NotebookLM — Segundo Cérebro de Engenharia & Aprendizado (via MCP & CLI `nlm`)

Integração direta e automatizada entre o **Google Antigravity** e o **Google NotebookLM (Gemini Notebook)** utilizando o servidor **MCP (`gemini-notebook-mcp`)**, a CLI **`nlm`** (`notebooklm-mcp-cli`) e o motor de automação **`brain_sync.py`**.

🔗 **Caderno Central no NotebookLM:** [`🧠 Segundo Cérebro — Engenharia & Aprendizado (Antigravity)`](https://notebook.google.com/notebook/4e930edb-9f8d-4a41-9987-52a3d1291720)
- **Notebook ID:** `4e930edb-9f8d-4a41-9987-52a3d1291720`
- **Alias configurado:** `cerebro`
- **Modo de IA do Caderno:** `learning_guide` (Guia de Aprendizado com respostas detalhadas)

---

## ⚙️ Arquitetura da Solução

1. **Wrapper Persistente ([`scripts/nlm_wrapper.py`](./scripts/nlm_wrapper.py) / `/home/antigravity/.gemini/nlm/nlm_wrapper.py`)**:
   - Auto-instala o pacote oficial `notebooklm-mcp-cli` (v0.16.2) caso a VM em nuvem do Antigravity seja recriada.
   - Sincroniza automaticamente os cookies e perfis de autenticação entre o armazenamento persistente (`/home/antigravity/.gemini/nlm/storage`) e o diretório local de execução (`~/.notebooklm-mcp-cli`), contornando restrições de `chmod` do sistema de arquivos FUSE.
   - Sanitiza a variável `NO_PROXY` (removendo `[::1]`) para evitar falhas de parser no `httpx`.
2. **Motor de Automação do Segundo Cérebro ([`scripts/brain_sync.py`](./scripts/brain_sync.py) / `/home/antigravity/.gemini/nlm/brain_sync.py`)**:
   - Conecta qualquer conversa e projeto do Antigravity ao caderno central no NotebookLM sem duplicar fontes (substitui automaticamente versões anteriores da mesma fonte ao atualizar).
   - Possui 3 pilares de sincronização:
     - **`💬 Chat & Decisões` (`sync-chat`)**: Registra o histórico da conversa, decisões arquiteturais, problemas encontrados e soluções aplicadas.
     - **`💻 Documentação de Código` (`sync-code`)**: Escaneia automaticamente o diretório do projeto, gera a árvore de arquivos, extrai assinaturas de classes/funções (`class`, `def`), docstrings e consolida o código-fonte comentado.
     - **`📘 Aprendizado` (`sync-learning`)**: Cria guias de estudo estruturados explicando os conceitos de engenharia de software aplicados na sessão.
3. **Skill Global ([`.agents/skills/nlm-skill/SKILL.md`](./.agents/skills/nlm-skill/SKILL.md))**:
   - Registrada internamente no Antigravity (`save_skill`) e versionada neste repositório, permitindo que **qualquer nova conversa** reconheça imediatamente os comandos do Segundo Cérebro e do servidor MCP.

---

## 🚀 Como Usar em Qualquer Conversa do Antigravity

### 1. Em Conversas Novas (Linguagem Natural)
Em qualquer **nova conversa** do Antigravity, a `nlm-skill` já vem carregada automaticamente. No final da conversa, você pode escolher entre:

- **Alimentar o Caderno Central (`🧠 Segundo Cérebro`)**:
  > *"Sincronize esta conversa, a documentação de código do projeto e o aprendizado com o meu Segundo Cérebro no NotebookLM."*
- **Criar um Notebook NOVO exclusivo para aquele chat/projeto**:
  > *"Crie um novo notebook no NotebookLM com tudo que falamos neste chat, a documentação do código e um guia de aprendizado."*
- **Gerar materiais de estudo (Podcast, Quiz, Flashcards, Mapa Mental)**:
  > *"Crie um podcast (Audio Overview) ou um quiz no meu Segundo Cérebro do NotebookLM sobre a arquitetura deste projeto."*

### 2. Em Conversas Antigas (Abertas antes da criação da Skill)
Conversas antigas não têm a `nlm-skill` na lista inicial de skills do prompt, mas **compartilham a mesma pasta `/home/antigravity/.gemini/nlm/`**. Para usar em uma conversa antiga, basta colar no chat antigo:

- **Para enviar a conversa antiga ao Segundo Cérebro:**
  > *"Salve um resumo completo de tudo que conversamos e decidimos neste chat em `/tmp/resumo.md` e execute no terminal: `python3 /home/antigravity/.gemini/nlm/brain_sync.py sync-chat --title 'Tema desta conversa' --file /tmp/resumo.md`"*
- **Para criar um Notebook NOVO a partir da conversa antiga:**
  > *"Salve o resumo desta conversa em `/tmp/resumo.md`, um guia de aprendizado em `/tmp/aprendizado.md` e execute no terminal: `python3 /home/antigravity/.gemini/nlm/brain_sync.py create-notebook --title 'Nome do Projeto' --chat-file /tmp/resumo.md --learning-file /tmp/aprendizado.md`"*

### Comandos Diretos da Automação (`brain_sync.py`)

```bash
# 1. Verificar o status e listar todas as fontes do Segundo Cérebro
python3 /home/antigravity/.gemini/nlm/brain_sync.py status

# 2. Sincronizar o resumo/decisões de um chat no Segundo Cérebro
python3 /home/antigravity/.gemini/nlm/brain_sync.py sync-chat \
  --title "Nome da Feature ou Sessão" \
  --file /tmp/resumo_chat.md

# 3. Gerar e sincronizar documentação completa de código de um repositório
python3 /home/antigravity/.gemini/nlm/brain_sync.py sync-code \
  --dir /home/antigravity/Zacydev/Antigravity-e-NotebookLM \
  --project "Antigravity-e-NotebookLM"

# 4. Publicar ou atualizar um Guia de Aprendizado
python3 /home/antigravity/.gemini/nlm/brain_sync.py sync-learning \
  --topic "Tema de Estudo" \
  --file /tmp/guia_aprendizado.md

# 5. Criar um caderno NOVO exclusivo no final da conversa (com chat + código + aprendizado)
python3 /home/antigravity/.gemini/nlm/brain_sync.py create-notebook \
  --title "Nome do Novo Caderno" \
  --chat-file /tmp/resumo_chat.md \
  --code-dir /caminho/do/projeto \
  --learning-file /tmp/guia_aprendizado.md
```

---

## 🛠️ Comandos da CLI Oficial (`nlm`)

```bash
# Verificar se a sessão Google continua válida
python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli login --check

# Listar todos os cadernos da conta
python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli notebook list

# Fazer uma pergunta diretamente ao Segundo Cérebro (usando o alias 'cerebro')
python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli notebook query cerebro "Faça um resumo das decisões técnicas e da arquitetura deste projeto"

# Gerar um Podcast (Audio Overview) ou Quiz a partir das fontes do Segundo Cérebro
python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli audio create cerebro --confirm
python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli quiz create cerebro --confirm
```
