# 📄 conversor-pdf-lote

Utilitário Python de linha de comando para converter múltiplos arquivos PDF em texto simples (`.txt`) de forma automatizada, preservando (ou não) a hierarquia de subpastas original.

---

## ✨ Funcionalidades

- Varredura recursiva de pastas em busca de PDFs (`.pdf` / `.PDF`)
- Extração de texto página a página via **pdfplumber**
- Preservação opcional da estrutura de subpastas no destino
- Cabeçalho informativo em cada TXT gerado (nome do arquivo, caminho e data)
- Renomeação automática para evitar sobrescritas
- Arquivo de log de erros gerado apenas quando necessário
- Exibição de progresso e resumo estatístico no terminal

---

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/<seu-usuario>/conversor-pdf-lote.git
cd conversor-pdf-lote

# (Opcional) Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows

# Instale a dependência
pip install pdfplumber
```

---

## 🖥️ Uso

```bash
# Conversão básica (TXT em <pasta_pdfs>/txt_convertidos/)
python conversor_pdf_lote.py pasta_pdfs

# Especificando a pasta de saída
python conversor_pdf_lote.py pasta_pdfs -o saida_txt

# Sem preservar a estrutura de subpastas
python conversor_pdf_lote.py pasta_pdfs -o saida_txt --sem-estrutura
```

### Parâmetros

| Argumento | Descrição |
|-----------|-----------|
| `pasta_entrada` | Pasta raiz contendo os PDFs (**obrigatório**) |
| `-o / --pasta-saida` | Destino dos TXT (padrão: `<pasta_entrada>/txt_convertidos`) |
| `--sem-estrutura` | Coloca todos os TXT na mesma pasta, sem replicar subpastas |

---

## 📦 Dependências

| Pacote | Versão mínima |
|--------|---------------|
| Python | 3.10+ |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | 0.9+ |

---

## 📂 Estrutura de saída

```
pasta_pdfs/
├── relatorio.pdf
├── subpasta/
│   └── contrato.pdf
└── txt_convertidos/          ← pasta de saída padrão
    ├── relatorio.txt
    ├── subpasta/
    │   └── contrato.txt
    └── conversao_log_20250421_103000.txt   ← criado apenas se houver erros
```

---

## ⚠️ Limitações

- PDFs baseados em imagem (escaneados sem camada de texto) não geram conteúdo extraível; a página é marcada como `[Página N — sem texto extraível]`.
- Para OCR de documentos escaneados, utilize ferramentas como [pytesseract](https://github.com/madmaze/pytesseract) em conjunto.

---

## 📝 Licença

[MIT](LICENSE)
