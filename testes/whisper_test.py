
from src.download_files import pac_files, download_from_pac
from src.process.audio_to_tex import parts
from configPy import Config, EnvManager
from json import dumps
import torch
import io
import torchaudio  # <--- Adicione esta linha


# Salvar resultado da transcriçã via whisper
files_dir = Config.get_dir_files()
output_dir = Config.get_dir_output()

# Output audio

output_audio_dir = output_dir.create_dir("audio")


# --- 1. Configuração e Checagem de Hardware ---
print("--- Configuração de Hardware ---")
print(f"CUDA disponível: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Dispositivo GPU: {torch.cuda.get_device_name(0)}")
else:
    print("Usando CPU.")

# --- 2. Gerenciamento de Ambiente e Tokens ---
print("\n--- Gerenciamento de Ambiente ---")
envMan = EnvManager() 
try:
    hf_token = envMan.get_hugging_face_token()
    print("Token Hugging Face carregado.")
except EnvironmentError as e:
    print(f"ERRO: {e}. O processo de diarização PODE FALHAR.")
    hf_token = None 

# --- 3. Download e Arquivo ---
print("\n--- Download de Arquivo ---")
pac = pac_files.get_files_by_year_link(1)
package = download_from_pac(pac, 5, use_temp=True) 

try:
    file_path = package.get_files()["audio"][1]
    print(f"Arquivo de áudio selecionado: {file_path.name}")
except IndexError:
    print("ERRO: Não foi possível encontrar o arquivo de áudio na posição [1].")
    exit()

file_name = file_path.stem

# diretório de output dda diarizção desse arquivo

# --- 4. parts de Pré-Processamento ---
print("\n--- Pré-Processamento de Áudio ---")
# O objeto final após o pré-processamento é necessário para a diarização
wav_buffer: io.BytesIO = parts.webm_to_pcmIO(file_path)
wav_buffer = parts.denoise_audioIO(wav_buffer)
wav_buffer = parts.apply_vad(wav_buffer)
print(f"Pré-processamento concluído. Tamanho final do buffer: {len(wav_buffer.getvalue())} bytes")


# --- 5. Diarização com Observação de Progresso ---
print("\n--- Diarização de Fala (Pyannote) ---")
if hf_token:
    # 1. Carrega a função de diarização (e o parts global, se ainda não estiver carregado)
    # NOTA: O parts global não é retornado, mas é acessado via closure.
    diarize_io_function = parts.get_diarization_function(hf_token)
    
    print("Iniciando diarização com barra de progresso...")
    
    try:
        # 2. CHAMA A FUNÇÃO. O ProgressHook é ATIVADO INTERNAMENTE.
        # A função retorna os segmentos e o DEVICE.
        segments_list, device_used = diarize_io_function(wav_buffer)
        
        # 3. Recalcula o tempo total para o dicionário final
        wav_buffer.seek(0)
        waveform, sample_rate = torchaudio.load(wav_buffer)
        total_time = len(waveform[0]) / sample_rate 
        
    except Exception as e:
        print(f"ERRO durante a diarização: {e}")
        segments_list = {} 
        # ... (restante do salvamento e fim do script) ...
    print("\nSegmentação Concluída:")
    print(f"Quantidade de segmentos: {len(segments_list)}")

    # salvar diarização como json
    # criar caminho

else:
    print("IGNORADO: Diarização requer o token HF que não foi encontrado.")


# Com a diarização feita, o buffer gerado pela detecção de voz é passado
# junto com a lista de segmentações para o whisper

wav_buffer.seek(0)

result = parts.transcribe_with_whisper(wav_buffer, segments_list)

print("\nTranscriçã concluída:")

print(dumps(result, indent=4))


print("\n--- Fim do Processamento ---")
input("Pressione Enter para finalizar o script.")
