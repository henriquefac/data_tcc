from dotenv import load_dotenv
import os
import json

from configPy import Config, DirManager

from src.tesserect_PIPE import OCR_blob_start

file_dir = Config.get_dir_files()
sample_dir = file_dir["samples"]

sample_atas_dir = sample_dir["atas"]

OCR_blob_start(sample_atas_dir)
