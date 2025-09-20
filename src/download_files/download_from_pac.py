from .download_methods import download_single_file_audio, download_single_file_pdf
from .get_data_pac import PacFULL, PacATAS, PacAUDIOS
from configPy import Config
from concurrent.futures import ThreadPoolExecutor, as_completed

N_WORKERS = 5

file_dir = Config.get_dir_files()

# diretório para amostras

samples_dir = file_dir.create_dir("samples")

# atas
samples_atas_dir = samples_dir.create_dir("atas")
# audios
samples_audios_dir = samples_dir.create_dir("audios")

# a partir da estrutura de um Pac, baixar arquivos


def download_pac_atas(pac_files:PacATAS, n_workers: int | None = None):
    if n_workers is None:
        n_workers = N_WORKERS
    #  root dir
    root_dir = samples_atas_dir.create_dir(f"{pac_files.hash}_sample")
    
    pac_structure = pac_files.structure

    dict_dirs = {key:root_dir.create_dir(key) for key in pac_structure}
    
    # percorre os arquivos e baixa
    files_tuples_args = []

    for key, tuplas in pac_structure.items():
        for url, filename in tuplas:
            files_tuples_args.append((url, filename, dict_dirs[key]))
    # fazer download em paralelo (faz <n_workers> por vez) e 
    # apenas avança para próximo batch quando todos os outro forem feitos
    for i in range(0, len(files_tuples_args), n_workers):
        batch = files_tuples_args[i:i+n_workers]
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [
                executor.submit(download_single_file_pdf, url, filename, output_dir)
                for url, filename, output_dir in batch
            ]
        for future in as_completed(futures):
            try:
                res = future.result()
                print(res)
            except Exception as e:
                print(f"Falha relacionado ao processo de paralização: {e}")


