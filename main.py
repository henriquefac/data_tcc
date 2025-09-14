from dotenv import load_dotenv
import os
import json

from configPy import Config, DirManager

from src.url_links import get_data_main

from src.download_files import download_all_audios, download_all_pdfs

from src.process_audio.methods import webm_to_wav, remove_silence


file_dir = Config.get_dir_files()
test_dir = file_dir.create_dir("test")

# audios_dir = file_dir["audios"]

test_file = test_dir["sessao-de-9-12-2021-Ata91.wav"] 


# output_wav = webm_to_wav(test_file, test_dir)
cut_wav = remove_silence(test_file, test_dir)
