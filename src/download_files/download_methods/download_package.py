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
    def get_package(cls, root_dir: DirManager, base_dir: DirManager| None = None) -> "PackageFiles":
        if not base_dir:
            return cls(root_dir, DirManager(root_dir.dir_path.parent))
        if isinstance(base_dir, TempDirManager):
            return TempPackageFiles(root_dir, base_dir)
        return cls(root_dir, base_dir)

    def iter_files(self) -> Iterator[Path]:
        """Itera recursivamente sobre todos os arquivos dentro de root_dir."""
        yield from self.root_dir.iter_all_files()

    def iter_dirs(self) -> Iterator[DirManager]:
        """Itera sobre os subdiretórios de root_dir (apenas um nível)."""
        yield from self.root_dir.iter_dirs()

    def get_files(self) -> dict[str, list[Path]]:
        """
        Retorna os arquivos organizados por tipo:
        - root_dir/
            -> 2020/, 2021/, ...   (estrutura simples: um único tipo → 'ata' ou 'audio')
        - root_dir/
            -> ata/2020/, ..., audio/2020/, ... (estrutura composta)
        """
        sub_dirs = list(self.iter_dirs())
        if not sub_dirs:
            return {}

        # Caso composto: ata/ e audio/
        if all(sd.dir_path.stem in ("ata", "audio") for sd in sub_dirs):
            return {
                "ata": list(sub_dirs[0].iter_all_files() if sub_dirs[0].dir_path.stem == "ata" else sub_dirs[1].iter_all_files()),
                "audio": list(sub_dirs[0].iter_all_files() if sub_dirs[0].dir_path.stem == "audio" else sub_dirs[1].iter_all_files()),
            }

        # Caso simples: apenas anos → decidir tipo pelo sufixo
        all_files = [f for sd in sub_dirs for f in sd.iter_all_files()]
        if not all_files:
            return {}

        if all_files[0].suffix in (".pdf", ".txt"):
            return {"ata": all_files}
        return {"audio": all_files}

  
@dataclass
class TempPackageFiles(PackageFiles):
    base_dir: TempDirManager

    def cleanup(self):
        """Remove os arquivos temporários do base_dir."""
        self.base_dir.cleanup()


# gerar package a partir de um objeto DirManager

