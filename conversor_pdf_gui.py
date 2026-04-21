"""
conversor_pdf_gui.py
Interface gráfica para o conversor de PDF em lote.

Dependências:
    pip install pdfplumber
    tkinter já vem com o Python padrão.

Uso:
    python conversor_pdf_gui.py
"""

import sys
import threading
from pathlib import Path
from datetime import datetime
from tkinter import (
    Tk, Frame, Label, Button, Entry, StringVar, BooleanVar,
    Checkbutton, Text, Scrollbar, filedialog, messagebox,
    ttk, END, DISABLED, NORMAL, WORD, RIGHT, Y, BOTH, LEFT,
    Canvas, PhotoImage
)

try:
    import pdfplumber
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
    import pdfplumber  # noqa: F811


# ──────────────────────────────────────────────────────────────────────────────
# Paleta e constantes de estilo
# ──────────────────────────────────────────────────────────────────────────────

CORES = {
    "bg":          "#0F1117",   # fundo principal
    "surface":     "#1C1E2A",   # painéis / cards
    "border":      "#2A2D3E",   # bordas sutis
    "accent":      "#4F8EF7",   # azul elétrico
    "accent_dark": "#3A6FD8",   # hover do accent
    "success":     "#3DDC97",   # verde sucesso
    "warn":        "#F5A623",   # laranja aviso
    "error":       "#F75F4F",   # vermelho erro
    "text":        "#E8EAF6",   # texto principal
    "text_muted":  "#6B7280",   # texto secundário
    "progress_bg": "#252839",   # fundo da barra de progresso
}

FONTE_TITULO  = ("Courier New", 22, "bold")
FONTE_LABEL   = ("Segoe UI", 10)
FONTE_LABEL_B = ("Segoe UI", 10, "bold")
FONTE_SMALL   = ("Segoe UI", 9)
FONTE_MONO    = ("Courier New", 9)


# ──────────────────────────────────────────────────────────────────────────────
# Lógica de conversão (reutiliza o núcleo do script CLI)
# ──────────────────────────────────────────────────────────────────────────────

class ConversorCore:
    """Núcleo de conversão reutilizável (sem UI)."""

    @staticmethod
    def encontrar_pdfs(pasta_entrada: Path, pasta_saida: Path) -> list[Path]:
        pdfs = set(pasta_entrada.rglob("*.pdf"))
        pdfs.update(pasta_entrada.rglob("*.PDF"))
        if pasta_saida.exists():
            pdfs = {p for p in pdfs if pasta_saida not in p.parents}
        return sorted(pdfs)

    @staticmethod
    def extrair_texto(caminho_pdf: Path) -> tuple[str, int, str | None]:
        try:
            partes: list[str] = []
            sep = "=" * 50
            with pdfplumber.open(caminho_pdf) as pdf:
                num_paginas = len(pdf.pages)
                for i, pagina in enumerate(pdf.pages, 1):
                    try:
                        txt = pagina.extract_text()
                        if txt and txt.strip():
                            partes.append(f"\n{sep}\nPágina {i} de {num_paginas}\n{sep}\n\n{txt}\n")
                        else:
                            partes.append(f"\n[Página {i} — sem texto extraível]\n")
                    except Exception as e:
                        partes.append(f"\n[Erro página {i}: {e}]\n")
            return "".join(partes).strip(), num_paginas, None
        except Exception as e:
            return "", 0, str(e)

    @staticmethod
    def caminho_saida(
        caminho_pdf: Path,
        pasta_entrada: Path,
        pasta_saida: Path,
        preservar_estrutura: bool,
    ) -> Path:
        if preservar_estrutura:
            relativo = caminho_pdf.relative_to(pasta_entrada)
            dest = pasta_saida / relativo.with_suffix(".txt")
        else:
            dest = pasta_saida / caminho_pdf.with_suffix(".txt").name
        dest.parent.mkdir(parents=True, exist_ok=True)
        base, n = dest, 1
        while dest.exists():
            dest = base.with_stem(f"{base.stem}_{n}")
            n += 1
        return dest

    @staticmethod
    def salvar(caminho_txt: Path, texto: str, caminho_pdf: Path) -> None:
        cab = (
            f"Arquivo original  : {caminho_pdf.name}\n"
            f"Caminho completo  : {caminho_pdf}\n"
            f"Data da conversão : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"{'=' * 60}\n\n"
        )
        caminho_txt.write_text(cab + texto, encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# Widgets customizados
# ──────────────────────────────────────────────────────────────────────────────

class EntryPath(Frame):
    """Campo de texto + botão 'Procurar'."""

    def __init__(self, master, placeholder: str, modo: str = "dir", **kw):
        super().__init__(master, bg=CORES["bg"], **kw)
        self._modo = modo

        self._var = StringVar()
        self._entry = Entry(
            self,
            textvariable=self._var,
            font=FONTE_MONO,
            bg=CORES["surface"],
            fg=CORES["text"],
            insertbackground=CORES["accent"],
            relief="flat",
            bd=0,
        )
        self._entry.insert(0, placeholder)
        self._entry.config(fg=CORES["text_muted"])
        self._entry.bind("<FocusIn>",  self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)
        self._placeholder = placeholder

        btn = Button(
            self,
            text="📂  Procurar",
            font=FONTE_SMALL,
            bg=CORES["accent"],
            fg="white",
            activebackground=CORES["accent_dark"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
            command=self._browse,
        )

        self._entry.pack(side=LEFT, fill=BOTH, expand=True, ipady=6, padx=(0, 6))
        btn.pack(side=RIGHT)

    def _on_focus_in(self, _):
        if self._entry.get() == self._placeholder:
            self._entry.delete(0, END)
            self._entry.config(fg=CORES["text"])

    def _on_focus_out(self, _):
        if not self._entry.get():
            self._entry.insert(0, self._placeholder)
            self._entry.config(fg=CORES["text_muted"])

    def _browse(self):
        if self._modo == "dir":
            path = filedialog.askdirectory(title="Selecionar pasta")
        else:
            path = filedialog.asksaveasfilename(title="Salvar em")
        if path:
            self._entry.delete(0, END)
            self._entry.insert(0, path)
            self._entry.config(fg=CORES["text"])

    def get(self) -> str:
        v = self._var.get().strip()
        return "" if v == self._placeholder else v


class LogBox(Frame):
    """Área de log rolável com suporte a tags de cor."""

    def __init__(self, master, **kw):
        super().__init__(master, bg=CORES["bg"], **kw)
        scroll = Scrollbar(self, bg=CORES["border"], troughcolor=CORES["surface"])
        self._text = Text(
            self,
            font=FONTE_MONO,
            bg=CORES["surface"],
            fg=CORES["text"],
            relief="flat",
            bd=0,
            state=DISABLED,
            wrap=WORD,
            yscrollcommand=scroll.set,
            padx=10,
            pady=8,
        )
        scroll.config(command=self._text.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self._text.pack(fill=BOTH, expand=True)

        # Tags de cor
        self._text.tag_config("ok",    foreground=CORES["success"])
        self._text.tag_config("err",   foreground=CORES["error"])
        self._text.tag_config("warn",  foreground=CORES["warn"])
        self._text.tag_config("info",  foreground=CORES["accent"])
        self._text.tag_config("muted", foreground=CORES["text_muted"])
        self._text.tag_config("bold",  font=FONTE_LABEL_B)

    def append(self, msg: str, tag: str = "") -> None:
        self._text.config(state=NORMAL)
        self._text.insert(END, msg + "\n", tag)
        self._text.see(END)
        self._text.config(state=DISABLED)

    def clear(self) -> None:
        self._text.config(state=NORMAL)
        self._text.delete("1.0", END)
        self._text.config(state=DISABLED)


# ──────────────────────────────────────────────────────────────────────────────
# Janela principal
# ──────────────────────────────────────────────────────────────────────────────

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("Conversor PDF → TXT em Lote")
        self.configure(bg=CORES["bg"])
        self.geometry("820x680")
        self.minsize(680, 540)
        self.resizable(True, True)

        self._cancelado = threading.Event()
        self._rodando   = False

        self._build_ui()
        self._center()

    # ── layout ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Cabeçalho ────────────────────────────────────────────────────────
        header = Frame(self, bg=CORES["bg"], pady=18)
        header.pack(fill="x", padx=28)

        Label(
            header,
            text="⬡  PDF → TXT",
            font=FONTE_TITULO,
            bg=CORES["bg"],
            fg=CORES["accent"],
        ).pack(side=LEFT)

        Label(
            header,
            text="conversor em lote",
            font=("Segoe UI", 10),
            bg=CORES["bg"],
            fg=CORES["text_muted"],
        ).pack(side=LEFT, padx=(10, 0), pady=(8, 0))

        # ── Separador ────────────────────────────────────────────────────────
        Canvas(self, height=1, bg=CORES["border"], highlightthickness=0).pack(fill="x")

        # ── Painel de configuração ───────────────────────────────────────────
        cfg = Frame(self, bg=CORES["surface"], padx=24, pady=18)
        cfg.pack(fill="x", padx=20, pady=(14, 6))

        self._entrada = self._campo(cfg, "📁  Pasta de entrada (PDFs):", 0)
        self._saida   = self._campo(cfg, "💾  Pasta de saída (TXTs):", 1, placeholder="Padrão: <entrada>/txt_convertidos")

        # Opções
        opts = Frame(cfg, bg=CORES["surface"])
        opts.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self._preservar = BooleanVar(value=True)
        Checkbutton(
            opts,
            text="Preservar estrutura de subpastas",
            variable=self._preservar,
            font=FONTE_LABEL,
            bg=CORES["surface"],
            fg=CORES["text"],
            activebackground=CORES["surface"],
            activeforeground=CORES["accent"],
            selectcolor=CORES["bg"],
            cursor="hand2",
        ).pack(side=LEFT)

        # ── Barra de progresso ───────────────────────────────────────────────
        prog_frame = Frame(self, bg=CORES["bg"], padx=20)
        prog_frame.pack(fill="x", pady=(4, 0))

        self._prog_label = Label(
            prog_frame,
            text="Aguardando...",
            font=FONTE_SMALL,
            bg=CORES["bg"],
            fg=CORES["text_muted"],
            anchor="w",
        )
        self._prog_label.pack(fill="x")

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=CORES["progress_bg"],
            background=CORES["accent"],
            darkcolor=CORES["accent"],
            lightcolor=CORES["accent"],
            bordercolor=CORES["border"],
            thickness=8,
        )
        self._progress = ttk.Progressbar(
            prog_frame,
            style="Custom.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
        )
        self._progress.pack(fill="x", pady=(4, 8))

        # ── Botões de ação ───────────────────────────────────────────────────
        btn_frame = Frame(self, bg=CORES["bg"], padx=20, pady=6)
        btn_frame.pack(fill="x")

        self._btn_iniciar = self._botao(btn_frame, "▶  Iniciar conversão", CORES["accent"], self._iniciar)
        self._btn_iniciar.pack(side=LEFT, padx=(0, 8))

        self._btn_cancelar = self._botao(btn_frame, "✕  Cancelar", CORES["error"], self._cancelar, estado=DISABLED)
        self._btn_cancelar.pack(side=LEFT, padx=(0, 8))

        self._botao(btn_frame, "🗑  Limpar log", CORES["text_muted"], self._limpar_log).pack(side=LEFT)

        # ── Área de log ──────────────────────────────────────────────────────
        Canvas(self, height=1, bg=CORES["border"], highlightthickness=0).pack(fill="x", pady=(6, 0))

        Label(
            self,
            text="  LOG DE EXECUÇÃO",
            font=("Segoe UI", 8, "bold"),
            bg=CORES["bg"],
            fg=CORES["text_muted"],
            anchor="w",
        ).pack(fill="x", padx=20, pady=(6, 2))

        self._log = LogBox(self)
        self._log.pack(fill=BOTH, expand=True, padx=20, pady=(0, 14))

        self._log.append("Pronto para converter. Selecione as pastas e clique em Iniciar.", "muted")

    def _campo(self, parent, label_txt: str, row: int, placeholder: str = "Clique em Procurar...") -> EntryPath:
        Label(
            parent,
            text=label_txt,
            font=FONTE_LABEL_B,
            bg=CORES["surface"],
            fg=CORES["text"],
            anchor="w",
        ).grid(row=row * 2, column=0, columnspan=2, sticky="w", pady=(0, 3) if row == 0 else (10, 3))

        entry = EntryPath(parent, placeholder=placeholder)
        entry.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(0, 2))
        parent.columnconfigure(0, weight=1)
        return entry

    @staticmethod
    def _botao(parent, texto, cor, cmd, estado=NORMAL) -> Button:
        return Button(
            parent,
            text=texto,
            font=FONTE_LABEL,
            bg=cor,
            fg="white",
            activebackground=cor,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=16,
            pady=7,
            command=cmd,
            state=estado,
        )

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - self.winfo_width())  // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    # ── controles ────────────────────────────────────────────────────────────

    def _iniciar(self):
        pasta_in = self._entrada.get()
        if not pasta_in:
            messagebox.showwarning("Atenção", "Selecione a pasta de entrada.")
            return

        pasta_in_path = Path(pasta_in)
        if not pasta_in_path.exists():
            messagebox.showerror("Erro", f"Pasta não encontrada:\n{pasta_in}")
            return

        pasta_out_str = self._saida.get()
        pasta_out = (
            pasta_in_path / "txt_convertidos"
            if not pasta_out_str
            else Path(pasta_out_str)
        )

        self._cancelado.clear()
        self._rodando = True
        self._btn_iniciar.config(state=DISABLED)
        self._btn_cancelar.config(state=NORMAL)
        self._log.clear()
        self._progress["value"] = 0
        self._prog_label.config(text="Iniciando...", fg=CORES["accent"])

        thread = threading.Thread(
            target=self._converter,
            args=(pasta_in_path, pasta_out, self._preservar.get()),
            daemon=True,
        )
        thread.start()

    def _cancelar(self):
        self._cancelado.set()
        self._log.append("⚠  Solicitação de cancelamento enviada...", "warn")

    def _limpar_log(self):
        self._log.clear()

    # ── conversão em thread ──────────────────────────────────────────────────

    def _converter(self, pasta_in: Path, pasta_out: Path, preservar: bool):
        log = self._log          # referência thread-safe para leitura
        prog = self._progress
        lbl  = self._prog_label

        def emit(msg, tag=""): self.after(0, log.append, msg, tag)
        def set_prog(v, t):
            self.after(0, lambda: prog.config(value=v))
            self.after(0, lambda: lbl.config(text=t))

        try:
            pasta_out.mkdir(parents=True, exist_ok=True)
            emit(f"📂  Saída: {pasta_out}", "info")

            pdfs = ConversorCore.encontrar_pdfs(pasta_in, pasta_out)
            if not pdfs:
                emit("❌  Nenhum PDF encontrado na pasta.", "err")
                return

            total = len(pdfs)
            emit(f"📚  {total} arquivo(s) encontrado(s)\n", "info")
            prog.config(maximum=total)

            ok = err = skip = pages = 0
            arquivo_log: Path | None = None

            for i, pdf in enumerate(pdfs, 1):
                if self._cancelado.is_set():
                    emit("\n⚠  Conversão cancelada pelo usuário.", "warn")
                    break

                set_prog(i, f"[{i}/{total}]  {pdf.name}")
                texto, npag, erro = ConversorCore.extrair_texto(pdf)

                if erro:
                    emit(f"  ❌  {pdf.name}  —  {erro}", "err")
                    err += 1
                    if arquivo_log is None:
                        arquivo_log = pasta_out / f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with arquivo_log.open("a", encoding="utf-8") as f:
                        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {pdf}: {erro}\n")
                    continue

                if not texto:
                    emit(f"  ⚠  {pdf.name}  —  sem texto extraível", "warn")
                    skip += 1
                    continue

                dest = ConversorCore.caminho_saida(pdf, pasta_in, pasta_out, preservar)
                ConversorCore.salvar(dest, texto, pdf)
                emit(f"  ✅  {pdf.name}  ({npag} pág.)  →  {dest.name}", "ok")
                ok += 1
                pages += npag

            # resumo
            emit("\n" + "─" * 54, "muted")
            emit("  RESUMO", "bold")
            emit("─" * 54, "muted")
            emit(f"  ✅  Convertidos  : {ok}", "ok")
            emit(f"  ❌  Com erro     : {err}", "err" if err else "muted")
            emit(f"  ⚠   Sem texto    : {skip}", "warn" if skip else "muted")
            emit(f"  📄  Total páginas: {pages}", "info")
            emit(f"  📁  Destino      : {pasta_out}", "info")
            if arquivo_log:
                emit(f"  📋  Log de erros : {arquivo_log}", "warn")
            emit("─" * 54, "muted")

            set_prog(total if not self._cancelado.is_set() else i,
                     "Concluído ✓" if not self._cancelado.is_set() else "Cancelado")

        except Exception as e:
            emit(f"\n❌  Erro inesperado: {e}", "err")

        finally:
            self._rodando = False
            self.after(0, lambda: self._btn_iniciar.config(state=NORMAL))
            self.after(0, lambda: self._btn_cancelar.config(state=DISABLED))


# ──────────────────────────────────────────────────────────────────────────────

def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
