from pathlib import Path
from configPy import DirManager
import pdfplumber
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def normalize_text(text: str, lowercase: bool = False) -> str:
    """
    Normaliza texto removendo acentos, espaços extras e linhas em branco.
    """
    # Normaliza acentuação
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))

    # Substitui múltiplos espaços/tabs por um espaço
    text = re.sub(r"\s+", " ", text)

    # Remove espaços extras em quebras de linha
    text = re.sub(r"\n\s+", "\n", text)

    # Remove linhas em branco
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines)

    if lowercase:
        text = text.lower()

    return text.strip()


def get_pdf_text(pdf_path: Path, output:DirManager ,preprocess: bool = True, lowercase: bool = False) -> str:
    """
    Extrai texto diretamente de um PDF (sem OCR).
    Pode aplicar pré-processamento opcional no texto.
    """
    namefile = pdf_path.stem

    try:
        output_file_path = output.create_file_path(namefile, "txt")
    except Exception as e:
        print(f"Arquivo já existe: {e}")

    texts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                texts.append(text.strip())

    raw_text = "\n\n".join(texts).strip()

    if preprocess:
        return normalize_text(raw_text, lowercase=lowercase)
    return raw_text

