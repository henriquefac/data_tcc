from configPy import Config, DirManager
from pathlib import Path
import pymupdf
files_dir = Config.get_dir_files()

# diretório de registro do texto das atas
atas_txt_dir = files_dir.create_dir("atas_txt")

# receb path do arquivo, extrai texto e armazena no diretório
def extract_tex_from_pdf(
    pdf_path: Path,
    dir_output: DirManager | None = None,
    output_filename: str | None = None
) -> Path:
    """
    Extrai o texto de um arquivo PDF e salva em um arquivo .txt.

    Args:
        pdf_path (Path): caminho para o arquivo PDF.
        dir_output (DirManager | None): diretório de saída. Se None, usa `atas_txt_dir`.
        output_filename (str | None): nome do arquivo de saída. Se None, usa o mesmo nome do PDF.

    Returns:
        Path: caminho para o arquivo .txt gerado.
    """
    if dir_output is None:
        dir_output = atas_txt_dir

    # nome do arquivo de saída
    if output_filename is None:
        output_filename = pdf_path.stem + ".txt"

    output_path = dir_output.dir_path / output_filename

    # abre o PDF
    doc = pymupdf.open(pdf_path)
    extracted_text = []

    for page in doc:
        text = page.get_text()
        if isinstance(text, bytes):  # garante string
            text = text.decode("utf-8", errors="ignore")
        print(text)
        extracted_text.append(text)
        

    doc.close()

    # salva o texto em UTF-8
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(extracted_text))

    return output_path
