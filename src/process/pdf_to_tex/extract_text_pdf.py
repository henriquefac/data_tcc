from .ocr import ocr_tesseract
from .pdf_to_text import get_pdf_text
from pathlib import Path

# emcapsulando métodos em uma função só
# funciona de forma unitária, uma entrada como um caminho 
# e uma saída de texto
def extract_text_from_single_pdf(file_path:Path):
    text = get_pdf_text(file_path)
    
    if not text:
        text = ocr_tesseract(file_path)
    return text

