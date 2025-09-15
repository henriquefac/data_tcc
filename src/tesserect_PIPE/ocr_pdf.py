from configPy import Config, DirManager
from pathlib import Path
from src.aux.temp_dir import TempDirManager, get_temp_dir, pdf_extract_images 
import re

from .pdf_to_txt import get_pdf_text

import pytesseract
from PIL import Image
import easyocr

file_dir = Config.get_dir_files()

# Diretório de output
output_dir = Config.get_dir_output()

atas_txt_dir = output_dir.create_dir("atas_txt")

easy_reader = easyocr.Reader(['pt'])

def get_text(pdf_path: Path, engine: str = "tesseract"):
    """
    Extrai texto de um PDF usando OCR.
    
    engine: "tesseract" ou "easyocr"
    """
    tmpDirMan = None
    img_f_list = None
  
    text = get_pdf_text(pdf_path)
    if text:
        return text

    try:
        tmpDirMan = get_temp_dir()
        img_f_list, tmpDirMan = pdf_extract_images(pdf_path, tempDirManager=tmpDirMan)
        
        full_text = ""

        if engine.lower() == "tesseract":
            for imgf in img_f_list:
                with Image.open(imgf) as img:
                    partial_text = pytesseract.image_to_string(img, lang="por", config='--psm 6')
                    partial_text = partial_text.replace("-\n", "").strip()
                    partial_text = re.sub(r"\s+", " ", partial_text)
                    full_text += partial_text + "\n"

        elif engine.lower() == "easyocr":
            for imgf in img_f_list:
                result = easy_reader.readtext(str(imgf))
                # Apenas texto
                partial_text = "\n".join([text for _, text, _ in result])
                partial_text = re.sub(r"\s+", " ", partial_text).strip()
                full_text += partial_text + "\n"
        else:
            raise ValueError(f"Engine OCR desconhecida: {engine}")

        return full_text

    finally:
        if tmpDirMan:
            tmpDirMan.cleanup()


def OCR_start(pdf_path: Path, output_dir: DirManager | None = None, engine: str = "tesseract"):
    if not output_dir:
        output_dir = atas_txt_dir

    output_dir = output_dir.create_dir(f"{engine}_ocr_{pdf_path.stem}")

    return OCR_start_aux(pdf_path, output_dir, engine)

def OCR_start_aux(pdf_path: Path, output_dir: DirManager | None = None, engine: str = "tesseract"):
    """
    Executa OCR no PDF e salva o resultado em um arquivo txt.
    """
    if not output_dir:
        output_dir = atas_txt_dir

    text_ocr = get_text(pdf_path, engine=engine)

    filename = pdf_path.stem
    file_output = output_dir.create_file_path(filename, suffix="txt", exist_ok=True)

    with open(file_output, "w", encoding="utf-8") as f:
        f.write(text_ocr)
    
    return file_output

def OCR_blob_start(pdf_dir_path: DirManager, output_dir: DirManager | None = None, engine: str = "tesseract"):
    if not output_dir:
        output_dir = atas_txt_dir

    output_dir = output_dir.create_dir(engine)

    OCR_blob_start_aux(pdf_dir_path, output_dir, engine)


def OCR_blob_start_aux(pdf_dir_path: DirManager, output_dir: DirManager | None = None, engine: str = "tesseract"):
    if not output_dir:
        output_dir = atas_txt_dir
    
    # final output
    output_dir = output_dir.create_dir(pdf_dir_path.dir_path.name) 
    
    # list_files
    list_files = [f for f in pdf_dir_path.list_files().values() if f.suffix.lower() == ".pdf"]
    
    
    for f in list_files:
        OCR_start_aux(f, output_dir, engine)

    list_subdirs = list(pdf_dir_path.list_dir().values())
    for dir in list_subdirs:
        OCR_blob_start_aux(dir, output_dir, engine)

