from src.download_files.download_methods import download_single_file_audio, download_single_file_pdf
from src.download_files.pac_files import PacFULL, PacATAS, PacAUDIOS, Pac
from src.download_files.aux import hash_map
from src.download_files.download_methods import PackageFiles, TempPackageFiles
from configPy import Config, DirManager, TempDirManager
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    use_temp: bool = False
)->PackageFiles| TempPackageFiles:
    if n_workers is None:
        n_workers = N_WORKERS

    base_dir = dir_sample_type

    if use_temp:
        temp_dir = TempDirManager.create_in_dir(dir_sample_type.dir_path)
        base_dir = temp_dir

    # root dir
    root_dir, pac_structure, dict_dirs = aux_root_dir(pac_files, base_dir)

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
    if not use_temp:
        if label == "atas":
            hash_map.add_hash_entry(pac_files.hash, samples_dir, ata=True)
        else:
            hash_map.add_hash_entry(pac_files.hash, samples_dir, audio=True)
    if use_temp:
        return TempPackageFiles(root_dir=root_dir, base_dir=base_dir)
    return PackageFiles(root_dir=root_dir, base_dir=base_dir)


def download_pac_full(pac_files: PacFULL, 
                      n_workers: int | None = None, 
                      use_temp: bool = False
    )->PackageFiles | TempPackageFiles:
    if n_workers is None:
        n_workers = N_WORKERS

    base_dir = samples_dir

    if use_temp:
        base_dir = TempDirManager.create_in_dir(base_dir)

    # diretórios raiz
    root_dir = base_dir.create_dir(f"{pac_files.hash}_sample")
    root_dir_atas = root_dir.create_dir("ata")
    root_dir_audios =root_dir.create_dir("audio")

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
    if not use_temp:    
        hash_map.add_hash_entry(pac_files.hash, samples_dir, ata=True, audio=True)
    if use_temp:
        return TempPackageFiles(root_dir=root_dir, base_dir=base_dir)
    return PackageFiles(root_dir=root_dir, base_dir=base_dir)


DOWNLOAD_DISPATCH = {
    PacATAS: (samples_dir, download_single_file_pdf, "atas"),
    PacAUDIOS: (samples_dir, download_single_file_audio, "audios"),
    PacFULL: (download_pac_full, None, "atas+audios"),
}

def download_from_pac(
    pac: PacATAS | PacAUDIOS | PacFULL,
    n_workers: int | None = None,
    use_temp: bool = False
) -> PackageFiles | TempPackageFiles:
    """
    Faz o download de um pacote PAC (ATAS, AUDIOS ou FULL),
    retornando um PackageFiles (persistente) ou TempPackageFiles (temporário).
    """
    for pac_cls, (arg1, arg2, label) in DOWNLOAD_DISPATCH.items():
        if isinstance(pac, pac_cls):
            try:
                if pac_cls is PacFULL:
                    # aqui arg1 é a função especializada
                    return arg1(pac, n_workers=n_workers, use_temp=use_temp)
                else:
                    # aqui arg1 é o diretório base e arg2 é a função de download
                    return _download_pac(
                        pac,
                        dir_sample_type=arg1,
                        download_fn=arg2,
                        label=label,
                        n_workers=n_workers,
                        use_temp=use_temp,
                    )
            except Exception as e:
                raise RuntimeError(
                    f"Falha ao realizar o download do pac de {label} ({pac.hash}): {e}"
                ) from e

    raise TypeError(f"Tipo de pac {type(pac).__name__} não suportado.")
