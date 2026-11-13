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

> **Nota:** Se o repositório `/home/antigravity/Zacydev/Antigravity-e-NotebookLM` estiver montado na conversa, use o script `scripts/notebooklm_bridge.py`. Caso esteja em **outra conversa/projeto** sem esse repositório montado, use os comandos diretos do `gdrive` e `gdocs` abaixo.

### 1. Verificar o status das pastas do NotebookLM
- **Com o repositório montado:**
  ```bash
  python3 /home/antigravity/Zacydev/Antigravity-e-NotebookLM/scripts/notebooklm_bridge.py status
  ```
- **Em qualquer outra conversa (direto via `gdrive`):**
  ```bash
  gdrive readonly ls 1nJFhBGmuqzkFrN-_wFrfoG6dHdsjZQAW
  gdrive readonly ls 1qt-hBrfeUZKJq_ZzcU89TJUvt3RIR9XN
  ```

### 2. Enviar ou atualizar um documento para o NotebookLM (Antigravity → NotebookLM)
- **Com o repositório montado:**
  ```bash
  python3 /home/antigravity/Zacydev/Antigravity-e-NotebookLM/scripts/notebooklm_bridge.py push <caminho_do_arquivo.md> --title "Título da Fonte"
  ```
- **Em qualquer outra conversa (direto via `gdocs` + `gdrive`):**
  1. Para criar uma nova fonte em `01_Fontes_para_NotebookLM`:
     ```bash
     gdocs mutate import-md <arquivo.md> --title "Título da Fonte" --auto-fit-tables
     gdrive mutate mv <DOC_ID_CRIADO> 1nJFhBGmuqzkFrN-_wFrfoG6dHdsjZQAW
     ```
  2. Para atualizar uma fonte existente mantendo o mesmo link no NotebookLM:
     ```bash
     gdocs mutate import-md <arquivo.md> --update <DOC_ID_EXISTENTE> --auto-fit-tables
     ```

### 3. Empacotar um Repositório Inteiro como Fonte do NotebookLM
- **Com o repositório montado:**
  ```bash
  python3 /home/antigravity/Zacydev/Antigravity-e-NotebookLM/scripts/notebooklm_bridge.py bundle-repo --dir <diretorio_do_repo> --title "Fonte NotebookLM — Nome do Projeto"
  ```

### 4. Ler Notas Exportadas do NotebookLM (NotebookLM → Antigravity)
1. Liste os arquivos da pasta `1qt-hBrfeUZKJq_ZzcU89TJUvt3RIR9XN`:
   ```bash
   gdrive readonly ls 1qt-hBrfeUZKJq_ZzcU89TJUvt3RIR9XN
   ```
2. Leia o conteúdo diretamente com:
   ```bash
   gdocs readonly read <DOC_ID>
   ```
