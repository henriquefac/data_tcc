from src.download_files import pac_files, download_from_pac

pac = pac_files.get_files_by_year_url_link(1)
package = download_from_pac(pac, 5, True)

print(package.get_files())
