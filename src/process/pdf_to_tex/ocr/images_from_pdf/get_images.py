from pdf2image import convert_from_path
from pathlib import Path
from io import BytesIO
from PIL import Image


def get_images_buffer(pdf_path: Path, dpi: int = 300) -> list[BytesIO]:
    """
    Converte PDF em uma lista de buffers de imagens (PNG em memória).
    Não cria arquivos temporários em disco.
    """
    pdf_pages = convert_from_path(pdf_path, dpi=dpi)
    buffers: list[BytesIO] = []

    for page in pdf_pages:
        # escala de cinza para reduzir tamanho
        page = page.convert("L")
        # opcional: binarização (melhora OCR em alguns casos)
        # page = page.point(lambda x: 0 if x < 180 else 255, "1")

        buffer = BytesIO()
        page.save(buffer, format="PNG")
        buffer.seek(0)
        buffers.append(buffer)

    return buffers
