from pathlib import Path
import pdfplumber


def get_pdf_text(pdf_path: Path) -> str:
    """
    Extrai texto diretamente de um PDF (sem OCR).
    Retorna o texto concatenado de todas as páginas.
    """
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""  # evita None
            full_text += text.strip() + "\n\n"
    return full_text.strip()

