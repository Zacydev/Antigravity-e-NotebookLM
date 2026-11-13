# Antigravity + NotebookLM (via MCP & CLI `nlm`)

Integração direta entre o **Google Antigravity** e o **Google NotebookLM (Gemini Notebook)** utilizando o servidor **MCP (`gemini-notebook-mcp`)** e a CLI **`nlm`** (`notebooklm-mcp-cli`).

---

## 🚀 O que já está instalado e configurado no seu ambiente

1. **Pacote Oficial (`notebooklm-mcp-cli` v0.16.2)**:
   - Fornece o servidor MCP **`gemini-notebook-mcp`** (com 55 ferramentas para criar cadernos, adicionar fontes, fazer perguntas ao chat do caderno, gerar podcasts/áudios, vídeos, slides, mapas mentais e relatórios) e a CLI **`nlm`**.
2. **Wrapper Persistente (`/home/antigravity/.gemini/nlm/nlm_wrapper.py`)**:
   - Garante que o servidor MCP e suas credenciais salvas em `/home/antigravity/.gemini/nlm/storage` persistam entre todas as suas conversas do Antigravity.
3. **Configuração Global do Servidor MCP**:
   - Configurada em `~/.gemini/antigravity/mcp_config.json`, `~/.gemini/config/mcp_config.json` e [`.agents/mcp_config.json`](./.agents/mcp_config.json).
4. **Skill Oficial (`nlm-skill`)**:
   - Instalada globalmente no Antigravity e versionada em [`.agents/skills/nlm-skill/SKILL.md`](./.agents/skills/nlm-skill/SKILL.md).

---

## 🔐 Último Passo Obrigatório: Autenticar sua Conta do NotebookLM

Como o NotebookLM exige uma sessão autenticada da sua conta Google:

### Opção A — Se você estiver usando o Antigravity Web (neste chat em nuvem)
1. Abra o [NotebookLM](https://notebooklm.google.com/) no navegador do seu computador (já logado na sua conta Google).
2. Pressione **F12** (ou clique com o botão direito $\rightarrow$ **Inspecionar**) e vá na aba **Rede (Network)**.
3. Recarregue a página (`F5`), clique na primeira requisição para `notebooklm.google.com` (ou `notebook.google.com` / `batchexecute`), clique com o botão direito nela e escolha **Copiar $\rightarrow$ Copiar como cURL (Copy as cURL)** *(ou copie o valor do cabeçalho `Cookie:`)*.
4. Cole aqui no chat (ou envie em um arquivo `cookies.txt`) para o agente executar:
   ```bash
   python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli login --manual --file cookies.txt --storage file
   ```
   Suas credenciais serão validadas e salvas de forma persistente em `/home/antigravity/.gemini/nlm/storage` para todas as conversas!

### Opção B — Se você estiver usando o Antigravity IDE / CLI instalado no seu computador
No terminal do seu computador, basta rodar:
```bash
uv tool install notebooklm-mcp-cli
nlm login
nlm setup add antigravity
nlm skill install antigravity
```
O comando `nlm login` abrirá o seu navegador automaticamente para capturar a sessão.

---

## 🛠️ Comandos Principais

```bash
# Verificar status do login e listar seus cadernos do NotebookLM
python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli login --check
python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli notebook list

# Criar um caderno novo
python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli notebook create "Meu Projeto"

# Adicionar uma fonte (texto, URL, YouTube ou Google Drive)
python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli source add <NOTEBOOK_ID> --text "Conteúdo..." --title "Título da Fonte"

# Fazer uma pergunta diretamente ao caderno
python3 /home/antigravity/.gemini/nlm/nlm_wrapper.py cli notebook query <NOTEBOOK_ID> "Quais são os pontos principais?"
```
