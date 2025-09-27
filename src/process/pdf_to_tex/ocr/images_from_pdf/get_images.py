from configPy import TempDirManager
from pdf2image import convert_from_path
from pathlib import Path

def get_dir_images(pdf_path: Path)->TempDirManager:
    pdf_pages = convert_from_path(pdf_path, 500)
    
    temp_dir = TempDirManager()

    for i, page in enumerate(pdf_pages, start=1):

        filename = f"page_{i}"
        file_path = temp_dir.create_file_path(filename, "jpg")

        page.save(file_path, "JPEG")
    return temp_dir
