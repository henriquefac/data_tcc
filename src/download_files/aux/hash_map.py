from configPy import DirManager
import csv

def get_hash_map(dir: DirManager):
    try:
        return dir["hash_map.csv"]
    except Exception as e:
        print(f"Erro ao buscar 'hash_map.csv' em {dir.dir_path}: {e}")
    print("Criando hash_map vazio")

    filepath = dir.create_file_path("hash_map", "csv")
    
    with open(filepath, "w", encoding='utf-8') as file:
        file.write("hash,ata,audio\n")
    
    return filepath

def add_hash_ata(hash:str, dir: DirManager):
    hash_file_map = get_hash_map(dir)

    with open(hash_file_map, 'a', newline='') as file_csv:
        writer = csv.writer(file_csv)

        writer.writerow([hash, "1", "0"])

def add_hash_audio(hash:str, dir: DirManager):
    hash_file_map = get_hash_map(dir)

    with open(hash_file_map, 'a', newline='') as file_csv:
        writer = csv.writer(file_csv)

        writer.writerow([hash, "0", "1"])

def add_hash_ata_audio(hash: str, dir: DirManager):
    hash_file_map = get_hash_map(dir)
    
    with open(hash_file_map, 'a', newline='') as file_csv:
        writer = csv.writer(file_csv)

        writer.writerow([hash, "1", "1"])

