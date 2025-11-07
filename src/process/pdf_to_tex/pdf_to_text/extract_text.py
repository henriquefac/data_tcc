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


def get_pdf_text_aux(pdf_path: Path, preprocess: bool = True, lowercase: bool = False) -> None | str:
    """
    Extrai texto diretamente de um PDF (sem OCR).
    Pode aplicar pré-processamento opcional no texto.
    """
    texts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                texts.append(text.strip())

    raw_text = "\n\n".join(texts).strip()
  
    if not raw_text or len(raw_text.split()) < 20:
        return None
    if preprocess:
        return normalize_text(raw_text, lowercase=lowercase)
    return raw_text

def get_pdf_text(pdf_path: Path, preprocess: bool = True, lowercase: bool= False) -> None | str:
    try:
        return get_pdf_text_aux(pdf_path, preprocess, lowercase)
    except Exception as e:
        print(f"Erro ao realizar extração clássica do texto do pdf {pdf_path}: {e}")
        return ""
