from dotenv import load_dotenv
import os
import json

from configPy import Config, DirManager

from src.url_links import get_data_main
from src.download_files import download_all_audios, download_all_pdfs

# Deve buscrar as url e para baixar as atas de reunião
# e os links dos videos do youtube das sessões
get_data_main(True)



# baixar todas as atas dos links
download_all_pdfs()

# Baixar todos os audios
download_all_audios(10)
