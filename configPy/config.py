from pathlib import Path
from typing import Union, Iterator
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()


class DirManager:
    def __init__(self, dir_path: Union[Path, "DirManager", str]):
        if isinstance(dir_path, DirManager):
            self.dir_path = dir_path.dir_path
        else:
            self.dir_path = Path(dir_path).resolve()

        if not self.dir_path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {self.dir_path}")
        if not self.dir_path.is_dir():
            raise NotADirectoryError(f"Não é um diretório: {self.dir_path}")

    def exists(self) -> bool:
        return self.dir_path.exists()

    def is_empty(self) -> bool:
        return not any(os.scandir(self.dir_path))

    def list_dirs(self) -> dict[str, "DirManager"]:
        return {
            entry.name: DirManager(entry.path)
            for entry in os.scandir(self.dir_path)
            if entry.is_dir()
        }

    def list_files(self) -> dict[str, Path]:
        return {
            entry.name: Path(entry.path)
            for entry in os.scandir(self.dir_path)
            if entry.is_file()
        }

    def iter_dirs(self) -> Iterator["DirManager"]:
        for entry in os.scandir(self.dir_path):
            if entry.is_dir():
                yield DirManager(entry.path)

    def iter_files(self) -> Iterator[Path]:
        for entry in os.scandir(self.dir_path):
            if entry.is_file():
                yield Path(entry.path)

    def iter_all_files(self) -> Iterator[Path]:
        # mais rápido que recursão manual
        for root, _, files in os.walk(self.dir_path):
            for file in files:
                yield Path(root) / file

    def create_dir(self, name: str) -> "DirManager":
        new_dir: Path = self.dir_path / name
        new_dir.mkdir(parents=True, exist_ok=True)
        return DirManager(new_dir)

    def create_file_path(self, name: str, suffix: str, overwrite: bool = False) -> Path:
        new_file_path: Path = self.dir_path / f"{name}.{suffix}"
        if new_file_path.exists() and not overwrite:
            raise ValueError(f"O arquivo <{new_file_path}> já existe")
        return new_file_path

    def __getitem__(self, key: str) -> "DirManager":
        dirs = self.list_dirs()
        if key in dirs:
            return dirs[key]
        raise KeyError(f"Diretório '{key}' não encontrado em {self.dir_path}")

    def get_any(self, key: str) -> "DirManager | Path":
        # Busca mais rápida: primeiro nível, depois recursivo
        dirs = self.list_dirs()
        files = self.list_files()
        if key in dirs:
            return dirs[key]
        if key in files:
            return files[key]
        for sub_dir in dirs.values():
            try:
                return sub_dir.get_any(key)
            except KeyError:
                continue
        raise KeyError(f"'{key}' não encontrado em {self.dir_path} e subdiretórios")

    def __str__(self) -> str:
        return str(self.dir_path)

    def __repr__(self) -> str:
        return f"DirManager({self.dir_path})"


class TempDirManager(DirManager):
    def __init__(self, parent: Path | DirManager | str | None = None):
        if parent:
            parent_path = Path(parent) if not isinstance(parent, DirManager) else parent.dir_path
            self.tempdir = tempfile.TemporaryDirectory(dir=parent_path)
        else:
            self.tempdir = tempfile.TemporaryDirectory()
        super().__init__(self.tempdir.name)

    def cleanup(self):
        self.tempdir.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    @classmethod
    def create_in_dir(cls, parent: Path | DirManager | str) -> "TempDirManager":
        return cls(parent)


class Config:
    BASE_PATH = Path(os.getenv("PYTHONPATH", ".")).resolve()
    FILE_DIR_PATH = BASE_PATH / "files"
    SRC_DIR_PATH = BASE_PATH / "src"
    OUTPUT_FILES = FILE_DIR_PATH / "output"

    @classmethod
    def get_dir_files(cls) -> DirManager:
        return DirManager(cls.FILE_DIR_PATH)

    @classmethod
    def get_dir_src(cls) -> DirManager:
        return DirManager(cls.SRC_DIR_PATH)

    @classmethod
    def get_dir_output(cls) -> DirManager:
        return DirManager(cls.OUTPUT_FILES)
