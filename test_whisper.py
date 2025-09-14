from dotenv import load_dotenv
import os
import json

from configPy import Config, DirManager
from pathlib import Path

from src.url_links import get_data_main

from src.download_files import download_all_audios, download_all_pdfs

from src.process_audio.methods import webm_to_wav, remove_silence


file_dir = Config.get_dir_files()
test_dir = file_dir.create_dir("test")

test_transcription = file_dir.create_dir("transcription_json")

# audios_dir = file_dir["audios"]

test_file = test_dir["sessao-de-9-12-2021-Ata91_cut.wav"] 
namefile = test_file.stem

import whisper 

model = whisper.load_model("small")

result = model.transcribe(str(test_file), language="pt")

saida_json = test_transcription.create_file_path(namefile+"_small", "json")

with open(saida_json, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)


