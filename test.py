from src.download_files import (
get_files_by_year_link, get_files_by_year_url,
get_files_by_porcent, get_files_by_year_url_link, download_from_pac
)
pac_url = get_files_by_year_url(2)

print(pac_url.hash)
print(pac_url.structure)

print(download_from_pac(pac_url))
