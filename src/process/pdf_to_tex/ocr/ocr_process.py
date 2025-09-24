from configPy import Config, DirManager, TempDirManager
# em arquivos, vai ter output


# vai receber um diretório e nvegar entre todos os diretórios e arquivos pdf
# vai baixar e recriar os diretórios

def run(dir_root: DirManager, hash: str):
    # navegar entre arquivos. Se algum for pdf
    
    # lista de arquivos
    files_in_dir = [f for f in dir_root.iter_files() if f.suffix == ".pdf" ]
