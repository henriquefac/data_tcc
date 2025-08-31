from configPy import Config, DirManager
from pathlib import Path
files_dir = Config.get_dir_files()

def modify_file_names_in_dir(dir_name:str, char_target:str, char_output:str):
    target_dir = files_dir[dir_name]

    list_files = list(target_dir.list_files().values())

    for f in list_files:
        origin_sufix = f.suffix
        origin_parent = f.parent

        new_name = f.stem.replace(char_target, char_output)
        new_path = Path(f"{origin_parent}/{new_name}{origin_sufix}")
        

        if new_path.exists():
            print(f"Arquvo {new_path} já existe, pulando")
            continue
        f.rename(new_path)


