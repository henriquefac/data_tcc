
from src.process.audio_to_tex import process_single_audio
from src.download_files import pac_files, download_from_pac

from configPy import Config, EnvManager
from json import dumps

import torch
import torchaudio
import io

# Salvar resultados da transcrição via whisper
files_dir = Config.get_dir_files()
output_dir = Config.get_dir_output()

# Outpu para audios transcritos

output_audio_dir = output_dir.create_dir("audio_testes")

# Nome para arquivo final

final_name = "_base"

# --- 1. COnfiguração e Cheagem de hardware ---
print("--- Configurações de Hardware ---")
print(f"CUDA disponível: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Dispositivo GPU: {torch.cuda.get_device_name(0)}")
else:
    print("Usando CPU.")

# --- 2. Gerenciamento de ambiente e tokens ---
print("\n--- Gerenciamento de Ambiente ---")

hf_env = EnvManager.huggingface()

try:
    hf_token = hf_env.HF_TOKEN
    hf_diarize_model = hf_env.HF_DIARIZE_MODEL
    print("Token Hugging Face carregado.")

except EnvironmentError as e:
    print(f"Erro: {e}. O processo de diarização PODE FALHAR")
    hf_token = None


# --- 3. Donwload de arquivos ---
print("\n--- Download de Arquivo ---")

pac = pac_files.get_files_by_year_link(1)
package = download_from_pac(pac, 5)
print("\n---------------------------")
try:
    file_path = package.get_files()["audio"][1]
    print(f"Arquivo de áudio selecionado: {file_path.name}")
except IndexError:
    print("ERRO: não foi possível encontrar o arquivo de áudio na possição [1].")
    exit()

# nome do arquivo para salvar transcrição
file_name = file_path.stem

print("\n--- Realizando processamento ---")
result = process_single_audio(str(file_path))

transcription = result["transcription"]

# arquivo para salvar
# Assumindo que output_audio_dir.create_dir retorna o caminho completo do arquivo
file_final_name = output_audio_dir.create_file_path(f"{file_name}{final_name}", "txt")

print(f"Salvando em: {file_final_name}")

# AQUI ESTÁ A CORREÇÃO:
# 1. Adicionado encoding="utf-8" para garantir que caracteres especiais sejam salvos corretamente.
# 2. Adicionado o caractere de quebra de linha (\n) ao final de cada escrita.
with open(file_final_name, "w", encoding="utf-8") as file:
    
    for segment in transcription:
        start = segment["start"]
        end = segment["end"]
        speaker = segment["speaker"]
        text = segment["text"]
        
        # Correção: Adicionar \n ao final para garantir uma quebra de linha após cada segmento.
        file.write(f"[{speaker}, <{start}-{end}>]: {text}\n")

print("\n--- Transcirção concluída ---")

print("\n--- Fim do processamento ---")
input("Pressione Enter para finalizar o script ---")
