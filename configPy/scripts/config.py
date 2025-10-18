from pathlib import Path
import os

from .dir import DirManager


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


