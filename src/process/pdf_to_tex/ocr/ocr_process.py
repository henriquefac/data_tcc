from .images_from_pdf import get_images_buffer
from configPy import DirManager
from pathlib import Path
import pytesseract
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from io import BytesIO


# vai receber um diretório e nvegar entre todos os diretórios e arquivos pdf
# vai baixar e recriar os diretórios

# recebe um path (pdf) e diretório para armazenar o texto extraído

def clean_text(text: str) -> str:
    """
    Realiza o tratamento básico do texto OCR.
    """
    # remove hifenização por quebra de linha
    text = text.replace("-\n", "")
    # normaliza múltiplas quebras de linha
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    # remove espaços duplos
    text = re.sub(r"[ \t]+", " ", text)
    # remove espaços no início/fim
    text = text.strip()
    return text


def ocr_page(img_buffer: BytesIO, page_num: int) -> tuple[int, str]:
    """
    Realiza OCR em uma única página recebida como buffer.
    """
    with Image.open(img_buffer) as img:
        raw_text = pytesseract.image_to_string(img)
    return page_num, clean_text(raw_text)


def ocr_tesseract(path: Path, output: DirManager, dpi: int = 300, workers: int = 10) -> Path | None:
    namefile = path.stem
    try:
        output_file_path = output.create_file_path(namefile, "txt")
    except Exception as e:
        print(f"Arquivo já existe: {e}")
        return None
    print(f"Realzando ocr do seguinte arquivo: {path}")
    # converte PDF em imagens em memória
    pages = get_images_buffer(path, dpi=dpi)
    total = len(pages)
    results: list[tuple[int, str]] = []
  
    done = 0
    # OCR paralelo
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(ocr_page, pages[i], i+1): i+1
            for i in range(len(pages))
        }

        for future in as_completed(futures):
            try:
                page_num, text = future.result()
                
                results.append((page_num, text))
                done += 1
                print(f"[{done}/{total}] Página {page_num} processada")
            except Exception as e:
                print(f"Falha no OCR da página {futures[future]}: {e}")

    # junta os textos na ordem correta
    results.sort(key=lambda x: x[0])
    full_text = "\n\n".join(text for _, text in results)

    # salva no arquivo
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(full_text)

    return output_file_path
