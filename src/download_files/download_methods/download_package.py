# classe de objetos que serão cuspidas pelas funções de 
# download. Deve conseguir identificar identificar a estrutura 
# para dos arquivos. Retornar o Path dos arquivos.

# se for um TempDirManager, dar a opção de paagar a fonte dos arquivos

from dataclasses import dataclass
from configPy import DirManager, TempDirManager
from pathlib import Path
from typing import Iterator



@dataclass
class PackageFiles:
    root_dir: DirManager
    base_dir: DirManager

    @classmethod
    def get_package(cls, root_dir: DirManager, base_dir: DirManager) -> "PackageFiles":
        if isinstance(base_dir, TempDirManager):
            return TempPackageFiles(root_dir, base_dir)
        return cls(root_dir, base_dir)

    def iter_files(self) -> Iterator[Path]:
        """Itera sobre todos os arquivos dentro de root_dir."""
        yield from self.root_dir.iter_files()

    def iter_dirs(self) -> Iterator[DirManager]:
        """Itera sobre os subdiretórios de root_dir."""
        yield from self.root_dir.iter_dirs()

    def get_files(self) -> dict[str, list[Path]]:
        """
        Retorna os arquivos organizados por tipo.
        - Se root_dir tem subdiretórios → retorna {"ata": [...], "audio": [...]}
        - Se não tem → detecta pelo sufixo (.pdf → atas, senão áudios)
        """
        sub_dirs = list(self.iter_dirs())
        if sub_dirs:
            if len(sub_dirs) != 2:
                raise ValueError("Esperado exatamente 2 subdiretórios (atas, audios).")

            return {
                sub_dirs[0].dir_path.stem: list(sub_dirs[0].iter_files()),
                sub_dirs[1].dir_path.stem: list(sub_dirs[1].iter_files()),
            }

        files = list(self.iter_files())
        if not files:
            return {}

        if files[0].suffix in (".pdf", ".txt"):
            return {"ata": files}
        return {"audio": files}


@dataclass
class TempPackageFiles(PackageFiles):
    base_dir: TempDirManager

    def cleanup(self):
        """Remove os arquivos temporários do base_dir."""
        self.base_dir.cleanup()
