from dotenv import load_dotenv
import os
import json

from src.url_links import get_data_main

from src.download_files import download_all_audios, download_all_pdfs

from src.process_audio.convert_audio import convert_all_audio

from src.process_audio.convert_audio_seq import convert_all_audio_seq

from src.process_audio.remove_silence import cut_silence_from_audio 

from src.aux.rename_files import modify_file_names_in_dir 

# fluxo de dados

# buscar urls e links
# get_data_main(True)

# baixar atas de reunião
# download_all_pdfs()

# baixar áudios de videos
#download_all_audios(max_workers=5, donwload_if_exists=True)

# checar arquivo ruim

#arquivos_corrompidos = check_all_files(10)


# print(json.dumps(arquivos_corrompidos, indent=4))
# remover rquivos corrompidos

#for f in arquivos_corrompidos:
#    rm_file(f)

# convert_all_audio_seq()

# processar arquivos (remover silencio)
# cut_silence_from_audio(10)


# DESNECESSÀRIO

# modificar nome do arquivo, substituir caractere de todos os arquivos de uma pasta

dirs = ["atas", "audios"]

for dir in dirs:
    modify_file_names_in_dir(dir, "|", "-")
    modify_file_names_in_dir(dir, ".", "-")
