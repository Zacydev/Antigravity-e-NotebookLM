# Antigravity + NotebookLM Bridge

Integração oficial e automatizada entre o **Google Antigravity** e o **Google NotebookLM** utilizando o **Google Drive** e o **Google Docs** como ponte bidirecional de conhecimento.

---

## 🔗 Links Rápidos (Google Drive & Docs)

| Recurso | Finalidade | Link Direto |
| :--- | :--- | :--- |
| **Pasta Principal** | Raiz da integração no Google Drive | [Antigravity + NotebookLM](https://drive.google.com/drive/folders/1Ci8ZfsexsMavNEvuZkWVnKXauhMeOBVM) |
| **01_Fontes_para_NotebookLM** | Documentos gerados pelo Antigravity para adicionar como fontes no NotebookLM | [Abrir Pasta de Fontes](https://drive.google.com/drive/folders/1nJFhBGmuqzkFrN-_wFrfoG6dHdsjZQAW) |
| **02_Exportados_do_NotebookLM** | Notas, briefings e guias exportados do NotebookLM para o Antigravity ler | [Abrir Pasta de Exportados](https://drive.google.com/drive/folders/1qt-hBrfeUZKJq_ZzcU89TJUvt3RIR9XN) |
| **Hub de Conhecimento (Doc)** | Documento inicial pronto para ser conectado ao seu caderno no NotebookLM | [Hub de Conhecimento — Antigravity & NotebookLM](https://docs.google.com/document/d/1V_Vt_dCFflP9jljx2dO7Ky5-oV47lhWEtYgN4-EW9ZQ/edit) |

---

## ⚙️ Como Funciona na Prática

### 1. Do Antigravity para o NotebookLM (`push` / `bundle-repo`)
1. O Antigravity gera documentações, especificações ou pacotes de código do repositório e converte automaticamente para um **Google Doc nativo** dentro da pasta `01_Fontes_para_NotebookLM`.
2. No [NotebookLM](https://notebooklm.google.com/), você cria um caderno e escolhe **Adicionar fonte $\rightarrow$ Google Drive $\rightarrow$ Documentos** e seleciona o documento da pasta `01_Fontes_para_NotebookLM`.
3. Quando o Antigravity atualizar o documento (`push`), ele **mantém o mesmo ID do Google Doc** (registrado em `notebooklm_manifest.json`). Assim, dentro do NotebookLM, basta clicar em **Sincronizar com o Google Drive** na fonte!

### 2. Do NotebookLM para o Antigravity (`pull`)
1. Depois de gerar notas, resumos ou especificações no NotebookLM, exporte-as como **Google Docs** e mova para a pasta `02_Exportados_do_NotebookLM`.
2. Peça ao Antigravity: *"Leia a nota X da pasta do NotebookLM e implemente o código"* (ou execute `python3 scripts/notebooklm_bridge.py pull "Nome da Nota"`).

---

## 🛠️ Uso pelo Terminal (CLI)

O script [`scripts/notebooklm_bridge.py`](./scripts/notebooklm_bridge.py) automatiza todas as operações:

```bash
# 1. Ver o status e listar todos os documentos nas pastas do Drive
python3 scripts/notebooklm_bridge.py status

# 2. Enviar ou atualizar um arquivo Markdown local como Google Doc no Drive
python3 scripts/notebooklm_bridge.py push README.md --title "Documentação Antigravity e NotebookLM"

# 3. Empacotar toda a estrutura e arquivos de um repositório para o NotebookLM
python3 scripts/notebooklm_bridge.py bundle-repo --dir . --title "Fonte NotebookLM — Repositório Antigravity-e-NotebookLM"

# 4. Baixar um Google Doc exportado do NotebookLM para a pasta local notes/
python3 scripts/notebooklm_bridge.py pull "Hub de Conhecimento"
```

---

## 💬 Uso Direto pelo Chat do Antigravity (Skill Ativa)

A skill **`notebooklm-bridge`** já está instalada no seu ambiente Antigravity (e versionada em [`.agents/skills/notebooklm-bridge/SKILL.md`](./.agents/skills/notebooklm-bridge/SKILL.md)). Você pode pedir diretamente no chat:

- *"Envie um resumo deste repositório para a minha pasta do NotebookLM."*
- *"Crie um documento de arquitetura sobre [tema] e publique nas fontes do NotebookLM."*
- *"Quais arquivos estão na minha pasta do NotebookLM agora?"*
- *"Leia o documento que salvei na pasta de exportados do NotebookLM."*
