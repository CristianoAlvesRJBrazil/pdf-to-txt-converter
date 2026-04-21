# 📄 conversor-pdf-lote

Utilitário Python para converter múltiplos arquivos PDF em texto simples (`.txt`), disponível em duas interfaces: **linha de comando (CLI)** e **interface gráfica (GUI)**.

| Versão | Arquivo | Requer |
|--------|---------|--------|
| Linha de comando (CLI) | `conversor_pdf_lote.py` | `pdfplumber` |
| Interface gráfica (GUI) | `conversor_pdf_gui.py`  | `pdfplumber` + `tkinter` |

---

## ✨ Funcionalidades (ambas versões)

- Varredura recursiva de pastas em busca de PDFs (`.pdf` / `.PDF`)
- Extração de texto página a página via **pdfplumber**
- Preservação opcional da estrutura de subpastas no destino
- Cabeçalho informativo em cada TXT gerado (nome, caminho e data)
- Renomeação automática para evitar sobrescritas
- Log de erros gerado apenas quando necessário

### 🎯 Diferenciais por versão

| Funcionalidade | CLI | GUI |
|----------------|-----|-----|
| Terminal colorido | ✅ | ❌ (log com ícones) |
| Barra de progresso | ✅ (texto) | ✅ (widget visual) |
| Botão Cancelar | ❌ | ✅ (interrompe entre arquivos) |
| Botão Limpar log | ❌ | ✅ |
| Seletor de pastas visual | ❌ | ✅ |
| Log colorido em tempo real | ✅ (ANSI) | ✅ (ícones: ✅❌⚠️) |
| Janela redimensionável | N/A | ✅ |

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

# Para a GUI — tkinter (já vem com Python, exceto em algumas distros Linux):
# Ubuntu/Debian:
sudo apt install python3-tk

