---
name: notebooklm-bridge
description: Sincroniza documentos, repositórios, notas e fontes de pesquisa entre o Antigravity e o Google NotebookLM usando a ponte oficial do Google Drive e Google Docs. Use sempre que o usuário mencionar NotebookLM, pedir para enviar um resumo/código/documento para o NotebookLM, atualizar uma fonte do NotebookLM, ou ler notas/briefings exportados do NotebookLM no Drive.
---
# NotebookLM Bridge (via Google Drive & Google Docs)

Esta skill conecta o **Antigravity** ao **Google NotebookLM** usando pastas dedicadas no Google Drive do usuário e conversão nativa para Google Docs (`gdocs` + `gdrive`).

## Estrutura Configurada no Google Drive

- **Pasta Principal (`Antigravity + NotebookLM`)**:
  - ID: `1Ci8ZfsexsMavNEvuZkWVnKXauhMeOBVM`
  - URL: `https://drive.google.com/drive/folders/1Ci8ZfsexsMavNEvuZkWVnKXauhMeOBVM`
- **Fontes geradas pelo Antigravity para o NotebookLM (`01_Fontes_para_NotebookLM`)**:
  - ID: `1nJFhBGmuqzkFrN-_wFrfoG6dHdsjZQAW`
  - URL: `https://drive.google.com/drive/folders/1nJFhBGmuqzkFrN-_wFrfoG6dHdsjZQAW`
- **Notas exportadas do NotebookLM para o Antigravity (`02_Exportados_do_NotebookLM`)**:
  - ID: `1qt-hBrfeUZKJq_ZzcU89TJUvt3RIR9XN`
  - URL: `https://drive.google.com/drive/folders/1qt-hBrfeUZKJq_ZzcU89TJUvt3RIR9XN`
- **Documento Hub Inicial (`Hub de Conhecimento — Antigravity & NotebookLM`)**:
  - ID: `1V_Vt_dCFflP9jljx2dO7Ky5-oV47lhWEtYgN4-EW9ZQ`
  - URL: `https://docs.google.com/document/d/1V_Vt_dCFflP9jljx2dO7Ky5-oV47lhWEtYgN4-EW9ZQ/edit`

## Fluxos de Trabalho

### 1. Verificar o status das pastas do NotebookLM
No repositório `/home/antigravity/Zacydev/Antigravity-e-NotebookLM`, execute:
```bash
python3 scripts/notebooklm_bridge.py status
```

### 2. Enviar ou atualizar um documento Markdown para o NotebookLM (Antigravity → NotebookLM)
```bash
python3 scripts/notebooklm_bridge.py push <caminho_do_arquivo.md> --title "Título da Fonte"
```

### 3. Empacotar um Repositório Inteiro como Fonte do NotebookLM
```bash
python3 scripts/notebooklm_bridge.py bundle-repo --dir <diretorio_do_repo> --title "Fonte NotebookLM — Nome do Projeto"
```

### 4. Ler Notas Exportadas do NotebookLM (NotebookLM → Antigravity)
```bash
python3 scripts/notebooklm_bridge.py pull "<nome_ou_id_do_doc>"
```
