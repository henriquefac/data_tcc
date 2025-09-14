from configPy import Config, DirManager
from pathlib import Path
from src.process_atas import extract_tex_from_pdf

file_dir = Config.get_dir_files()
atas_dir = file_dir["atas"]
filetest = atas_dir["sessao-de-9-12-2021-Ata91.pdf"]

extract_tex_from_pdf(filetest)

