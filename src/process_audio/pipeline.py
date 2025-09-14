import tempfile
from configPy import Config, DirManager
import tempfile
from pathlib import Path
import uuid


files_dir = Config.get_dir_files()
temp_dir_root = files_dir.create_dir("temp_dir_root")
tempfile.tempdir = str(temp_dir_root.dir_path)

# essa classe deve reuir todas as funções para gerar um pipeline
# essas funções devem ser capazs de receber um arquivo e gerar um arquivo em de volta
class FunWrapper:
    _steps = []

    @classmethod
    def wrapper(cls, func):
        cls._steps.append(func)
        return func

    @classmethod
    def get_steps(cls):
        for func in cls._steps:
            yield func


class Pipeline():
    root = temp_dir_root
    single_id: uuid.UUID

    def __init__(self):
        self.single_id = uuid.uuid4()

    def run(self, input_path):
        # Path do dir temporário
        dir_temp_output = DirManager(tempfile.mkdtemp(prefix=str(self.single_id)+"_"))
        
        for func in FunWrapper.get_steps():
            _file_output = func(input_path, dir_temp_output)
