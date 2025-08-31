from pathlib import Path
from typing import Union
import os
from dotenv import load_dotenv

class DirManager():
    def __init__(self, dir_path: Union[Path, "DirManager"]):
        self.dir_path = Path(dir_path) if isinstance(dir_path, (str, Path)) else dir_path.dir_path
    
    def has_files(self)->bool:
        return any(self.dir_path.iterdir())

    def list_dir(self)->dict[str, 'DirManager']:
        return {dir.name : DirManager(dir) for dir in self.dir_path.iterdir() if dir.is_dir()}
    def list_files(self)->dict[str, Path]:
        return {file.name : file for file in self.dir_path.iterdir() if file.is_file()}
    def create_dir(self, name:str)->'DirManager':
        new_dir: Path = self.dir_path / name
        new_dir.mkdir(parents=True, exist_ok=True)
        return DirManager(new_dir)
    def create_file_path(self, name:str, suffix:str, exist_ok=False)->Path:
        new_file_path: Path = self.dir_path / f"{name}.{suffix}"
        if new_file_path.exists() and exist_ok:
            raise ValueError(f"O arquivo <{new_file_path}> já existe")
        return new_file_path
    def __str__(self) -> str:
        return str(self.dir_path)
    def __repr__(self) -> str:
        return f"DirManager({self.dir_path})"
    def __getitem__(self, key: str)-> 'DirManager':
        dirs = self.list_dir()
        files = self.list_files()
        if key in dirs:
            return dirs[key]
        if key in files:
            return files[key]
        for sub_dir in dirs.values():
            try:
                return sub_dir[key]
            except KeyError:
                continue
        raise KeyError(f"({key}) não foi encontrado em ({self.dir_path}) e subdiretórios")

class Config:
    # Paths
    BASE_PATH = Path(os.getenv("PYTHONPATH")).resolve()
    FILE_DIR_PATH = BASE_PATH / "files"
    SRC_DIR_PATH = BASE_PATH / "src"

    @classmethod
    def get_dir_files(cls) -> DirManager:
        return DirManager(cls.FILE_DIR_PATH)
    @classmethod
    def get_dir_src(cls) -> DirManager:
        return DirManager(cls.SRC_DIR_PATH)


