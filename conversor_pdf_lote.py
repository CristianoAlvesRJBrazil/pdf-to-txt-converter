"""
conversor_pdf_lote.py
Converte arquivos PDF para TXT em lote, preservando (opcionalmente) a estrutura de subpastas.

Uso:
    python conversor_pdf_lote.py <pasta_entrada>
    python conversor_pdf_lote.py <pasta_entrada> -o <pasta_saida>
    python conversor_pdf_lote.py <pasta_entrada> -o <pasta_saida> --sem-estrutura

Dependências:
    pip install pdfplumber
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    print("❌ Dependência ausente: instale com  pip install pdfplumber")
    sys.exit(1)


class ConversorPDFLote:
    """Converte todos os PDFs de uma pasta (e subpastas) para arquivos TXT."""

    def __init__(
        self,
        pasta_entrada: str,
        pasta_saida: str | None = None,
        preservar_estrutura: bool = True,
    ) -> None:
        """
        Args:
            pasta_entrada: Pasta raiz contendo os arquivos PDF.
            pasta_saida: Pasta de destino dos TXT.
                         Padrão: ``<pasta_entrada>/txt_convertidos``.
            preservar_estrutura: Se ``True``, replica a hierarquia de subpastas
                                 no destino.
        """
        self.pasta_entrada = Path(pasta_entrada)
        self.preservar_estrutura = preservar_estrutura
        self.pasta_saida = (
            self.pasta_entrada / "txt_convertidos"
            if pasta_saida is None
            else Path(pasta_saida)
        )

        # Estatísticas
        self.arquivos_processados: int = 0
        self.arquivos_com_erro: int = 0
        self.arquivos_ignorados: int = 0
        self.total_paginas: int = 0

        # O arquivo de log só é criado quando há erros (lazy init)
        self._arquivo_log: Path | None = None

    # ------------------------------------------------------------------
    # Propriedade de log (criada sob demanda)
    # ------------------------------------------------------------------

    @property
    def arquivo_log(self) -> Path:
        if self._arquivo_log is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._arquivo_log = self.pasta_saida / f"conversao_log_{timestamp}.txt"
        return self._arquivo_log

    # ------------------------------------------------------------------
    # Preparação
    # ------------------------------------------------------------------

    def criar_pastas(self) -> None:
        """Valida a pasta de entrada e cria a pasta de saída."""
        if not self.pasta_entrada.exists():
            raise FileNotFoundError(
                f"❌ Pasta de entrada não encontrada: {self.pasta_entrada}"
            )
        self.pasta_saida.mkdir(parents=True, exist_ok=True)
        print(f"📂 Pasta de saída: {self.pasta_saida}")

    # ------------------------------------------------------------------
    # Descoberta de arquivos
    # ------------------------------------------------------------------

    def encontrar_pdfs(self) -> list[Path]:
        """Retorna lista ordenada e sem duplicatas de todos os PDFs encontrados."""
        pdfs = set(self.pasta_entrada.rglob("*.pdf"))
        pdfs.update(self.pasta_entrada.rglob("*.PDF"))

        # Exclui PDFs que já estejam dentro da própria pasta de saída
        if self.pasta_saida.exists():
            pdfs = {p for p in pdfs if self.pasta_saida not in p.parents}

        return sorted(pdfs)

    # ------------------------------------------------------------------
    # Extração de texto
    # ------------------------------------------------------------------

    def extrair_texto_pdf(
        self, caminho_pdf: Path
    ) -> tuple[str, int, str | None]:
        """
        Extrai o texto de todas as páginas do PDF.

        Returns:
            Tupla ``(texto, num_paginas, mensagem_de_erro)``.
            Em caso de sucesso, ``mensagem_de_erro`` é ``None``.
        """
        try:
            partes: list[str] = []
            with pdfplumber.open(caminho_pdf) as pdf:
                num_paginas = len(pdf.pages)
                separador = "=" * 50

                for i, pagina in enumerate(pdf.pages, start=1):
                    try:
                        texto_pagina = pagina.extract_text()
                        if texto_pagina and texto_pagina.strip():
                            partes.append(
                                f"\n{separador}\n"
                                f"Página {i} de {num_paginas}\n"
                                f"{separador}\n\n"
                                f"{texto_pagina}\n"
                            )
                        else:
                            partes.append(f"\n[Página {i} — sem texto extraível]\n")
                    except Exception as exc:  # noqa: BLE001
                        partes.append(f"\n[Erro ao extrair página {i}: {exc}]\n")

            return "".join(partes).strip(), num_paginas, None

        except Exception as exc:  # noqa: BLE001
            return "", 0, str(exc)

    # ------------------------------------------------------------------
    # Caminhos de saída
    # ------------------------------------------------------------------

    def definir_caminho_saida(self, caminho_pdf: Path) -> Path:
        """
        Calcula o caminho do TXT correspondente ao PDF.

        Garante unicidade adicionando sufixo numérico se necessário.
        """
        if self.preservar_estrutura:
            relativo = caminho_pdf.relative_to(self.pasta_entrada)
            caminho_txt = self.pasta_saida / relativo.with_suffix(".txt")
        else:
            caminho_txt = self.pasta_saida / caminho_pdf.with_suffix(".txt").name

        caminho_txt.parent.mkdir(parents=True, exist_ok=True)

        # Evita sobrescrever arquivos existentes
        base = caminho_txt
        contador = 1
        while caminho_txt.exists():
            caminho_txt = base.with_stem(f"{base.stem}_{contador}")
            contador += 1

        return caminho_txt

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def salvar_texto(
        self, caminho_txt: Path, texto: str, caminho_pdf: Path
    ) -> None:
        """Grava o texto com cabeçalho informativo no arquivo de destino."""
        cabecalho = (
            f"Arquivo original  : {caminho_pdf.name}\n"
            f"Caminho completo  : {caminho_pdf}\n"
            f"Data da conversão : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"{'=' * 60}\n\n"
        )
        caminho_txt.write_text(cabecalho + texto, encoding="utf-8")

    def _log_erro(self, caminho_pdf: Path, erro: str) -> None:
        """Acrescenta uma linha de erro no arquivo de log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with self.arquivo_log.open("a", encoding="utf-8") as log:
            log.write(f"[{timestamp}] {caminho_pdf}: {erro}\n")

    # ------------------------------------------------------------------
    # Processamento
    # ------------------------------------------------------------------

    def processar_pdf(self, caminho_pdf: Path) -> None:
        """Processa um único PDF e exibe o resultado no terminal."""
        print(f"  📄 {caminho_pdf.name} ... ", end="", flush=True)

        texto, num_paginas, erro = self.extrair_texto_pdf(caminho_pdf)

        if erro:
            print(f"❌  {erro}")
            self.arquivos_com_erro += 1
            self._log_erro(caminho_pdf, erro)
            return

        if not texto:
            print("⚠️  nenhum texto extraível")
            self.arquivos_ignorados += 1
            return

        caminho_txt = self.definir_caminho_saida(caminho_pdf)
        self.salvar_texto(caminho_txt, texto, caminho_pdf)

        print(f"✅  {num_paginas} pág. → {caminho_txt.name}")
        self.arquivos_processados += 1
        self.total_paginas += num_paginas

    def processar_todos(self) -> None:
        """Descobre e processa todos os PDFs, exibindo progresso."""
        print("\n🔍 Procurando arquivos PDF...")
        pdfs = self.encontrar_pdfs()

        if not pdfs:
            print("❌ Nenhum arquivo PDF encontrado na pasta especificada.")
            return

        total = len(pdfs)
        print(f"📚 {total} arquivo(s) encontrado(s)\n")

        for i, pdf in enumerate(pdfs, start=1):
            print(f"[{i:>{len(str(total))}}/{total}]", end=" ")
            self.processar_pdf(pdf)

        self._exibir_resumo()

    def _exibir_resumo(self) -> None:
        """Exibe estatísticas ao final da execução."""
        linha = "=" * 60
        print(f"\n{linha}")
        print("📊  RESUMO DA CONVERSÃO")
        print(linha)
        print(f"  ✅ Processados com sucesso : {self.arquivos_processados}")
        print(f"  ❌ Com erro                : {self.arquivos_com_erro}")
        print(f"  ⚠️  Sem texto extraível    : {self.arquivos_ignorados}")
        print(f"  📄 Total de páginas        : {self.total_paginas}")
        print(f"  📁 Destino                 : {self.pasta_saida}")
        if self.arquivos_com_erro > 0:
            print(f"  📋 Log de erros            : {self.arquivo_log}")
        print(linha)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Converte todos os PDFs de uma pasta para arquivos TXT.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python conversor_pdf_lote.py pasta_pdfs
  python conversor_pdf_lote.py pasta_pdfs -o saida_txt
  python conversor_pdf_lote.py pasta_pdfs -o saida_txt --sem-estrutura
""",
    )
    parser.add_argument(
        "pasta_entrada",
        help="Pasta contendo os arquivos PDF.",
    )
    parser.add_argument(
        "-o", "--pasta-saida",
        metavar="PASTA",
        help="Destino dos TXT (padrão: <pasta_entrada>/txt_convertidos).",
    )
    parser.add_argument(
        "--sem-estrutura",
        action="store_false",
        dest="preservar_estrutura",
        help="Coloca todos os TXT na mesma pasta, sem replicar subpastas.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        conversor = ConversorPDFLote(
            pasta_entrada=args.pasta_entrada,
            pasta_saida=args.pasta_saida,
            preservar_estrutura=args.preservar_estrutura,
        )
        conversor.criar_pastas()
        conversor.processar_todos()

    except KeyboardInterrupt:
        print("\n\n⚠️  Processamento interrompido pelo usuário.")
        sys.exit(1)
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"\n❌ Erro fatal: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
