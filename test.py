from src.download_files import (download_from_pac, 
    get_files_by_year_url, get_files_by_year_link, get_files_by_year_url_link)


pac_url = get_files_by_year_url_link(4)

print(pac_url.hash)
print(pac_url.structure)

print(download_from_pac(pac_url))
