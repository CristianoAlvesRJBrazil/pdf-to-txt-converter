# 📄 conversor-pdf-lote

Utilitário Python para converter múltiplos arquivos PDF em texto simples (`.txt`), disponível em duas interfaces:

| Versão | Arquivo | Requer |
|--------|---------|--------|
| Linha de comando (CLI) | `conversor_pdf_lote.py` | `pdfplumber` |
| Interface gráfica (GUI) | `conversor_pdf_gui.py`  | `pdfplumber` + `tkinter` |

---

## ✨ Funcionalidades

- Varredura recursiva de pastas em busca de PDFs (`.pdf` / `.PDF`)
- Extração de texto página a página via **pdfplumber**
- Preservação opcional da estrutura de subpastas no destino
- Cabeçalho informativo em cada TXT gerado (nome, caminho e data)
- Renomeação automática para evitar sobrescritas
- Log de erros gerado apenas quando necessário
- **GUI**: barra de progresso, log colorido em tempo real, botão Cancelar

---

## 🚀 Instalação

```bash
git clone https://github.com/<seu-usuario>/conversor-pdf-lote.git
cd conversor-pdf-lote

# (Opcional) Ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# Dependência principal
pip install pdfplumber

# Para a GUI — tkinter já vem com o Python, mas em algumas distros Linux é separado:
# Ubuntu/Debian:
sudo apt install python3-tk
```

---

## 🖥️ Interface Gráfica (GUI)

```bash
python conversor_pdf_gui.py
```

### Recursos da GUI

- Seletor de pastas com diálogo nativo do SO
- Checkbox para preservar/ignorar estrutura de subpastas
- Barra de progresso em tempo real
- Log colorido: ✅ sucesso · ❌ erro · ⚠️ sem texto
- Botão **Cancelar** funcional (interrompe entre arquivos)
- Botão **Limpar log**
- Janela redimensionável e centralizada na tela

---

## ⌨️ Linha de Comando (CLI)

```bash
# Conversão básica
python conversor_pdf_lote.py pasta_pdfs

# Especificando destino
python conversor_pdf_lote.py pasta_pdfs -o saida_txt

# Sem preservar subpastas
python conversor_pdf_lote.py pasta_pdfs -o saida_txt --sem-estrutura
```

### Parâmetros

| Argumento | Descrição |
|-----------|-----------|
| `pasta_entrada` | Pasta raiz com os PDFs (**obrigatório**) |
| `-o / --pasta-saida` | Destino dos TXT (padrão: `<entrada>/txt_convertidos`) |
| `--sem-estrutura` | Todos os TXT na mesma pasta, sem replicar subpastas |

---

## 📂 Estrutura de saída

```
pasta_pdfs/
├── relatorio.pdf
├── subpasta/
│   └── contrato.pdf
└── txt_convertidos/
    ├── relatorio.txt
    ├── subpasta/
    │   └── contrato.txt
    └── log_20250421_103000.txt   ← criado apenas se houver erros
```

---

## 📦 Dependências

| Pacote | Versão mínima | Observação |
|--------|---------------|------------|
| Python | 3.10+ | necessário para `str \| None` |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | 0.9+ | extração de texto |
| tkinter | — | GUI — incluído no Python; no Linux instale `python3-tk` |

---

## ⚠️ Limitações

PDFs baseados em imagem (escaneados sem camada de texto) não geram conteúdo extraível. Para OCR, utilize [pytesseract](https://github.com/madmaze/pytesseract) em conjunto.

---

## 📝 Licença

[MIT](LICENSE)
