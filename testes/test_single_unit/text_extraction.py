from src.download_files import pac_files, download_from_pac
from src.process.pdf_to_tex import extract_text_from_single_pdf

pac = pac_files.get_files_by_year_url(1)
package = download_from_pac(pac, 5, True)

pdfs_paths = package.get_files()
test_file = pdfs_paths["ata"][0]

text = extract_text_from_single_pdf(test_file)
print(text)
