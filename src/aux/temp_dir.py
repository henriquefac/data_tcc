from configPy import Config, DirManager
import tempfile
from pathlib import Path

import math
from pdf2image import convert_from_path

# cria um diretório temporário e devolve o manager
def get_temp_dir():
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_manager = TempDirManager(temp_dir)
    return temp_dir_manager


class TempDirManager(DirManager):
    def __init__(self, tempdir: tempfile.TemporaryDirectory):
        self.tempdir = tempdir
        super().__init__(Path(tempdir.name))  # o DirManager trabalha com Path

    def cleanup(self):
        """Remove o diretório temporário e todos os arquivos dentro."""
        self.tempdir.cleanup()

# Par um pdf, popula um diretório temporário com imagens
def pdf_extract_images(pdf_path: Path, tempDirManager: TempDirManager | None = None):
    if not tempDirManager:
        tempDirManager = get_temp_dir()

    pdf_pages = convert_from_path(pdf_path, 300)
    digits = int(math.log10(len(pdf_pages))) + 1
    
    image_file_list = []

    for i, page in enumerate(pdf_pages, start=1):
        filename = tempDirManager.create_file_path(f"page_{i:0{digits}d}", "png")
        
        page = page.convert("L")  # grayscale
        
        # page = page.point(lambda x: 0 if x < 128 else 255)
        
        page.save(str(filename), "PNG")
        image_file_list.append(filename)

    return image_file_list, tempDirManager
