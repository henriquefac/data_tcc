from configPy import DirManager
import csv

def get_hash_map(dir: DirManager):
    try:
        return dir.get_any("hash_map.csv")
    except Exception as e:
        print(f"Erro ao buscar 'hash_map.csv' em {dir.dir_path}: {e}")
    print("Criando hash_map vazio")

    filepath = dir.create_file_path("hash_map", "csv")
    
    with open(filepath, "w", encoding='utf-8') as file:
        file.write("hash,ata,audio\n")
    
    return filepath


def add_hash_entry(hash: str, dir: DirManager, ata: bool = False, audio: bool = False):
    hash_file_map = get_hash_map(dir)

    # Lê todas as linhas já existentes
    with open(hash_file_map, "r", encoding="utf-8") as file_csv:
        lines = list(csv.reader(file_csv))

    # Dicionário temporário para facilitar atualização
    data = {row[0]: row[1:] for row in lines[1:]}  # ignora cabeçalho

    # Atualiza ou insere
    if hash in data:
        current_ata, current_audio = map(int, data[hash])
        data[hash] = [
            str(max(current_ata, int(ata))),
            str(max(current_audio, int(audio))),
        ]
    else:
        data[hash] = [str(int(ata)), str(int(audio))]

    # Reescreve o arquivo inteiro
    with open(hash_file_map, "w", newline="", encoding="utf-8") as file_csv:
        writer = csv.writer(file_csv)
        writer.writerow(["hash", "ata", "audio"])
        for h, values in data.items():
            writer.writerow([h] + values)

def hash_exists(hash: str, dir: DirManager) -> bool:
    """
    Verifica se um hash já está registrado no hash_map.csv.
    Retorna True se existir, False caso contrário.
    """
    hash_file_map = get_hash_map(dir)

    with open(hash_file_map, "r", encoding="utf-8") as file_csv:
        reader = csv.reader(file_csv)
        next(reader, None)  # pula o cabeçalho
        for row in reader:
            if row and row[0] == hash:
                return True
    return False

