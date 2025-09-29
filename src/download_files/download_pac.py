from concurrent.futures import ThreadPoolExecutor, as_completed
from configPy import Config, DirManager, TempDirManager
from src.download_files.download_methods import (
    download_single_file_audio,
    download_single_file_pdf,
    PackageFiles,
    TempPackageFiles,
)
from src.download_files.pac_files import PacFULL, PacATAS, PacAUDIOS, Pac
from src.download_files.aux import hash_map

N_WORKERS = 5
file_dir = Config.get_dir_files()
samples_dir = file_dir.create_dir("samples")


# -----------------------------
# Funções utilitárias
# -----------------------------
def create_root_and_subdirs(base_dir: DirManager, pac_hash: str, subfolders: list[str] | None = None):
    """Cria o diretório raiz do PAC e subdiretórios opcionais"""
    root_dir = base_dir.create_dir(f"{pac_hash}_sample")
    subdirs = {name: root_dir.create_dir(str(name)) for name in subfolders} if subfolders else {}
    return root_dir, subdirs


def execute_downloads(file_args: list[tuple], download_fn, n_workers: int):
    """Executa downloads em paralelo com ThreadPoolExecutor"""
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(download_fn, url, filename, out_dir) for url, filename, out_dir in file_args]
        for future in as_completed(futures):
            try:
                print(future.result())
            except Exception as e:
                print(f"Falha no download: {e}")


# -----------------------------
# Funções de download
# -----------------------------
def _download_pac(
    pac_files: Pac,
    dir_sample_type: DirManager,
    download_fn,
    label: str,
    n_workers: int | None = None,
    use_temp: bool = False,
) -> PackageFiles | TempPackageFiles:
    if n_workers is None:
        n_workers = N_WORKERS

    base_dir: DirManager = TempDirManager.create_in_dir(dir_sample_type.dir_path) if use_temp else dir_sample_type

    # Checa se hash já existe antes de criar diretórios
    if hash_map.hash_exists(pac_files.hash, base_dir):
        root_dir, _ = create_root_and_subdirs(base_dir, pac_files.hash)
        return PackageFiles(root_dir, base_dir)

    # Cria root e subdiretórios
    root_dir, dict_dirs = create_root_and_subdirs(base_dir, pac_files.hash, list(pac_files.structure.keys()))

    # Prepara lista de arquivos para download
    files_args = [
        (url, filename, dict_dirs[key])
        for key, tuplas in pac_files.structure.items()
        for url, filename in tuplas
    ]

    # Executa download
    execute_downloads(files_args, download_fn, n_workers)

    # Atualiza hash_map
    if not use_temp:
        if label == "atas":
            hash_map.add_hash_entry(pac_files.hash, samples_dir, ata=True)
        else:
            hash_map.add_hash_entry(pac_files.hash, samples_dir, audio=True)

    return TempPackageFiles(root_dir, base_dir) if use_temp else PackageFiles(root_dir, base_dir)


def download_pac_full(pac_files: PacFULL, n_workers: int | None = None, use_temp: bool = False) -> PackageFiles | TempPackageFiles:
    if n_workers is None:
        n_workers = N_WORKERS

    base_dir: DirManager = TempDirManager.create_in_dir(samples_dir.dir_path) if use_temp else samples_dir

    # Cria diretórios raiz
    root_dir, subdirs = create_root_and_subdirs(base_dir, pac_files.hash, ["ata", "audio"])

    if hash_map.hash_exists(pac_files.hash, base_dir):
        root_dir, _ = create_root_and_subdirs(base_dir, pac_files.hash)
        return PackageFiles(root_dir, base_dir)

    dict_dirs_atas = {key: subdirs["ata"].create_dir(str(key)) for key in pac_files.structure}
    dict_dirs_audios = {key: subdirs["audio"].create_dir(str(key)) for key in pac_files.structure}

    # Prepara listas de downloads
    files_args_atas = [
        (url_ata, filename, dict_dirs_atas[key])
        for key, tuplas in pac_files.structure.items()
        for link_audio, url_ata, filename in tuplas
    ]
    files_args_audios = [
        (link_audio, filename, dict_dirs_audios[key])
        for key, tuplas in pac_files.structure.items()
        for link_audio, url_ata, filename in tuplas
    ]

    # Executa downloads
    execute_downloads(files_args_atas, download_single_file_pdf, n_workers)
    execute_downloads(files_args_audios, download_single_file_audio, n_workers)

    if not use_temp:
        hash_map.add_hash_entry(pac_files.hash, samples_dir, ata=True, audio=True)

    return TempPackageFiles(root_dir, base_dir) if use_temp else PackageFiles(root_dir, base_dir)


# -----------------------------
# Dispatch para tipos de PAC
# -----------------------------
DOWNLOAD_DISPATCH = {
    PacATAS: (samples_dir, download_single_file_pdf, "atas"),
    PacAUDIOS: (samples_dir, download_single_file_audio, "audios"),
    PacFULL: (download_pac_full, None, "atas+audios"),
}


def download_from_pac(
    pac: PacATAS | PacAUDIOS | PacFULL,
    n_workers: int | None = None,
    use_temp: bool = False,
) -> PackageFiles | TempPackageFiles:
    """
    Faz o download de um pacote PAC (ATAS, AUDIOS ou FULL),
    retornando um PackageFiles (persistente) ou TempPackageFiles (temporário).
    """
    for pac_cls, (arg1, arg2, label) in DOWNLOAD_DISPATCH.items():
        if isinstance(pac, pac_cls):
            try:
                if pac_cls is PacFULL:
                    return arg1(pac, n_workers=n_workers, use_temp=use_temp)
                else:
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
