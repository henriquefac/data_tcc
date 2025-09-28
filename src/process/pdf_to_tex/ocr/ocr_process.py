from .images_from_pdf import get_dir_images
from configPy import TempDirManager, DirManager
from pathlib import Path
import pytesseract
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import re



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


def ocr_page(img_path: Path, page_num: int) -> tuple[int, str]:
    """
    Realiza OCR em uma única página (retorna página e texto limpo).
    """
    with Image.open(img_path) as img:
        raw_text = pytesseract.image_to_string(img)
    return page_num, clean_text(raw_text)


def ocr_tesseract(path: Path, output: DirManager, dpi: int = 300, workers: int = 4) -> Path | None:
    """
    Executa OCR em um PDF e salva o texto processado em arquivo .txt
    """
    namefile = path.stem
    try:
        output_file_path = output.create_file_path(namefile, "txt")
    except Exception as e:
        print(f"Arquivo já existe: {e}")
        return None

    # converte PDF em imagens
    temp_dir_imgs, num_pages = get_dir_images(path, dpi=dpi)

    results: list[tuple[int, str]] = []

    # OCR paralelo
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(ocr_page, temp_dir_imgs.list_files()[f"page_{i}.jpg"], i): i
            for i in range(1, num_pages + 1)
        }

        for future in as_completed(futures):
            try:
                page_num, text = future.result()
                results.append((page_num, text))
            except Exception as e:
                print(f"Falha no OCR da página {futures[future]}: {e}")

    # junta os textos na ordem correta
    results.sort(key=lambda x: x[0])
    full_text = "\n\n".join(text for _, text in results)

    # salva no arquivo
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(full_text)
  
    temp_dir_imgs.cleanup()

    return output_file_path


