from src.process.audio_to_text_prototype import pipelines
from src.process.pdf_to_tex import extract_text_from_single_pdf
from src.download_files import pac_files, download_from_pac
from configPy import Config, DirManager
from pathlib import Path


OUTPUT_FORMAT = "txt"

# Diretório de output
output_dir = Config.get_dir_output()

# output para áudios
output_audio_dir = output_dir.create_dir("audio")
# output para atas
output_ata_dir = output_dir.create_dir("ata")

# pacs de arquivos 
# 5 arquivos para cada ano (são 6 anos diponíveis: [2020 -> 2025])
# e cada arquivo vem em pares
# total de 60 arquivos de amostra
pac = pac_files.get_files_by_year_url_link(5)
package = download_from_pac(pac, n_workers=10) # vai baixar todos os arquvios como um diretório temporário

all_files = package.get_files()


# arquivos de audio 
audio_files = all_files["audio"]

# arquivos pdf
pdf_files = all_files["ata"]

def convert_ata_to_text(ata:Path, output_path: Path | None):
    if output_path is None:
        return ""

    return extract_text_from_single_pdf(ata)

def convert_audio_to_text(audio: Path, output_path: Path | None):
    if output_path is None:
        return ""

    return pipelines.process_single_audio(str(audio))

# função para aplicar em cada combinação de arquivos as trnasformações
def convertert_tuples_files(ata:Path, audio: Path, 
    output_ata: DirManager, output_audio: DirManager):

    baseName = ata.stem

    outputAtaFile = None
    outputAudioFile = None

    # caminhos de saída de cada arquivo
    try:
        outputAtaFile = output_ata.create_file_path(name=baseName, suffix=OUTPUT_FORMAT, overwrite= False)
    except Exception as e:
        print(f"O arquivo referente a {ata.name} convertido para texto já existe em {output_ata.dir_path.name}: {e}")

    try:
        outputAudioFile = output_audio.create_file_path(name=baseName, suffix=OUTPUT_FORMAT, overwrite=False)
    except Exception as e:
        print(f"O arquivo referente a {audio.name} convertido para texto já existe em {output_audio.dir_path.name}: {e}")

    try:
        # converter ata para texto
        textAta = convert_ata_to_text(ata, outputAtaFile)
        if textAta:
            with open(outputAtaFile, "w", encoding="utf-8") as of:
                of.write(textAta)
            print(f"PDF convertido e salvo em {outputAtaFile.name}")
        else:
            print(f"Ata {ata.name} está vazia ou deu algo errado na extração")
            raise Exception("Falha ao processar ata")
        # converter audio para texto
        textAudio = convert_audio_to_text(audio, outputAudioFile)
        if textAudio:
            with open(outputAudioFile, "w", encoding="utf-8") as of:
                of.write(textAudio)
            print(f"Áudio convertido e salvo em {outputAudioFile.name}")
        else:
            print(f"Áudio {audio.name} retornou vazio")
            raise Exception("Falha ao processar áudio")
    
    except Exception as e:
        print(f"Erro ao processar conjunto de dados ({ata.name},{audio.name}): {e}")

total_pairs = min(len(pdf_files), len(audio_files))

for i in range(total_pairs):
    ata = pdf_files[i]
    audio = audio_files[i]
    convertert_tuples_files(ata=ata, audio=audio,output_ata=output_ata_dir, output_audio=output_audio_dir)
