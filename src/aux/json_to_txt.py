from configPy import Config, DirManager
import json
from pathlib import Path

files_dir = Config.get_dir_files()

# Diretório para carregar arquivos
transcription_txt_dir = files_dir.create_dir("transcription_txt")

def jsonToTxt(json_path: Path, output_txt_dir:DirManager = transcription_txt_dir,
              time_stamp=False):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # arquivo de saída (pode sobreescrever)
    filename = json_path.stem
    outputfile = output_txt_dir.create_file_path(filename, "txt")

    lines = []
    for segment in data.get("segments", []):
        if time_stamp:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()
            lines.append(f"[{start:.2f}->{end:.2f}] {text}")
        else:
            lines.append(segment["text"].strip())
        
    full_text = "\n".join(lines)
   
    with open(outputfile, "w", encoding="utf-8") as f:
        f.write(full_text)

    return full_text
