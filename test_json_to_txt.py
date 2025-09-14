import json

from configPy import Config, DirManager
from pathlib import Path


from src.aux import json_to_txt as jt

file_dir = Config.get_dir_files()
test_transcription = file_dir.create_dir("transcription_json")


test_txt_trasncription = file_dir.create_dir("transcription_txt")

test_file = test_transcription["sessao-de-9-12-2021-Ata91_cut_small.json"]


text = jt.jsonToTxt(test_file,test_txt_trasncription, True)

print(text)
