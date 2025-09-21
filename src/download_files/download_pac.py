from .download_methods import download_single_file_audio, download_single_file_pdf
from .get_data_pac import PacFULL, PacATAS, PacAUDIOS, Pac
from configPy import Config, DirManager
from concurrent.futures import ThreadPoolExecutor, as_completed
from .aux import hash_map
N_WORKERS = 5

file_dir = Config.get_dir_files()

# diretório para amostras
samples_dir = file_dir.create_dir("samples")


def aux_root_dir(pac_files: Pac, dir_sample_type: DirManager):
    root_dir = dir_sample_type.create_dir(f"{pac_files.hash}_sample")
    pac_structure = pac_files.structure
    dict_dirs = {key: root_dir.create_dir(str(key)) for key in pac_structure}
    return root_dir, pac_structure, dict_dirs


def _download_pac(
    pac_files: Pac,
    dir_sample_type: DirManager,
    download_fn,
    label: str,
    n_workers: int | None = None,
):
    if n_workers is None:
        n_workers = N_WORKERS

    # root dir
    root_dir, pac_structure, dict_dirs = aux_root_dir(pac_files, dir_sample_type)

    # monta lista de arquivos
    files_tuples_args = [
        (url, filename, dict_dirs[key])
        for key, tuplas in pac_structure.items()
        for url, filename in tuplas
    ]

    # download em batches
    for i in range(0, len(files_tuples_args), n_workers):
        batch = files_tuples_args[i : i + n_workers]
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [
                executor.submit(download_fn, url, filename, output_dir)
                for url, filename, output_dir in batch
            ]
        for future in as_completed(futures):
            try:
                res = future.result()
                print(res)
            except Exception as e:
                print(f"Falha relacionado ao processo de paralização: {e}")
    
    if label == "atas":
        hash_map.add_hash_ata(pac_files.hash, samples_dir)
    else:
        hash_map.add_hash_ata(pac_files.hash, samples_dir)

    return root_dir


def download_pac_full(pac_files: PacFULL, n_workers: int | None = None):
    if n_workers is None:
        n_workers = N_WORKERS

    # diretórios raiz
    root_dir = samples_dir.create_dir(f"{pac_files.hash}_sample")
    root_dir_atas = root_dir.create_dir("atas")
    root_dir_audios =root_dir.create_dir("audios")

    pac_structure = pac_files.structure

    dict_dirs_atas = {key: root_dir_atas.create_dir(str(key)) for key in pac_structure}
    dict_dirs_audios = {key: root_dir_audios.create_dir(str(key)) for key in pac_structure}

    file_tuple_args_atas = [
        (url_ata, filename, dict_dirs_atas[key])
        for key, tuplas in pac_structure.items()
        for link_audio, url_ata, filename in tuplas
    ]

    file_tuple_args_audios = [
        (link_audio, filename, dict_dirs_audios[key])
        for key, tuplas in pac_structure.items()
        for link_audio, url_ata, filename in tuplas
    ]

    def process_downloads(file_args, download_fn, label):
        for i in range(0, len(file_args), n_workers):
            batch = file_args[i : i + n_workers]
            with ThreadPoolExecutor(max_workers=n_workers) as executor:
                futures = [
                    executor.submit(download_fn, url, filename, output_dir)
                    for url, filename, output_dir in batch
                ]
            for future in as_completed(futures):
                try:
                    res = future.result()
                    print(res)
                except Exception as e:
                    print(f"Falha no download de {label}: {e}")

    process_downloads(file_tuple_args_atas, download_single_file_pdf, "atas")
    process_downloads(file_tuple_args_audios, download_single_file_audio, "áudios")
    
    hash_map.add_hash_ata_audio(pac_files.hash, samples_dir)
    return root_dir_atas, root_dir_audios


DOWNLOAD_DISPATCH = {
    PacATAS: (samples_dir, download_single_file_pdf, "atas"),
    PacAUDIOS: (samples_dir, download_single_file_audio, "audios"),
    PacFULL: (download_pac_full, None, "atas+audios"),
}


def download_from_pac(pac: PacATAS | PacAUDIOS | PacFULL, n_workers: int | None = None):
    hash = pac.hash
    for pac_cls, (arg1, arg2, label) in DOWNLOAD_DISPATCH.items():
        if isinstance(pac, pac_cls):
            try:
                if pac_cls is PacFULL:
                    dir_res = arg1(pac, n_workers)  # aqui arg1 é a função
                else:
                    dir_res = _download_pac(pac, arg1, arg2, label, n_workers)  # dir, fn
                return f"Download de pac de {label} feito em: {dir_res}"
            except Exception as e:
                return f"Falha ao realizar o download do pac de {label} {hash}: {e}"

    return f"Tipo de pac {type(pac).__name__} não suportado."
