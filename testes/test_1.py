from src.download_files import pac_files

pacs_10 = list(pac_files.get_files_by_porcent_link(pac_files.DotValue.DOT10))

print(pacs_10[0])
