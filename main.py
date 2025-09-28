from src.download_files import download_from_pac, pac_files
from src.process.pdf_to_tex import extract_text_from_pdf


pacs = list(pac_files.get_files_by_porcent_url(pac_files.DotValue.DOT5))


package = download_from_pac(pacs[0], use_temp=True)

print(package.root_dir)


result = extract_text_from_pdf(package)

package.cleanup()
