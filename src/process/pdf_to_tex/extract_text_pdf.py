from .ocr import ocr_tesseract
from .pdf_to_text import get_pdf_text
from pathlib import Path
from src.download_files.download_methods import PackageFiles, TempPackageFiles
from configPy import Config

output_dir = Config.get_dir_output()


def extract_text_from_pdf(package: PackageFiles | TempPackageFiles):
    results = {}
    files_path_pdf = package.get_files().get("ata", [])

    for f in files_path_pdf:
        pdf_path = Path(f)

        # 1. tenta extração convencional
        text = get_pdf_text(pdf_path, output=output_dir)

        # 2. se falhar ou vier muito curto, cai para OCR
        if not text or len(text.split()) < 10:
            text = ocr_tesseract(pdf_path, output=output_dir)

        results[pdf_path.name] = text

    return results
