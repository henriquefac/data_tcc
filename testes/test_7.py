from src.download_files import pac_files, download_from_pac
from src.process.audio_to_tex import pipeline
from configPy import Config, EnvManager, TempDirManager
from json import dumps
import torch
import io
import torchaudio  # <--- Adicione esta linha
from pyannote.audio.pipelines.utils.hook import ProgressHook 

import pickle

# Salvar json resultado da diarização
files_dir = Config.get_dir_files()
diarizacao_test_dir = files_dir.create_dir("diarizacao_data")

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
package = download_from_pac(pac, 5) 

try:
    file_paths = package.get_files()["audio"]
    print(f"Lista de arquivos de áudio adiquirida: quantidade {len(file_paths)}")
except IndexError:
    print("ERRO: Não foi possível encontrar o arquivo de áudio na posição [1].")
    exit()

wav_buffer: io.BytesIO = io.BytesIO()

for file_path in file_paths:

    file_name = file_path.stem

    # diretório de output dda diarizção desse arquivo
    diarizacao_output_dir = diarizacao_test_dir.create_dir(f"{file_name}_diarizacao")
    
    wav_buffer.seek(0)

    # --- 4. Pipeline de Pré-Processamento ---
    print("\n--- Pré-Processamento de Áudio ---")
    # O objeto final após o pré-processamento é necessário para a diarização
    wav_buffer: io.BytesIO = pipeline.webm_to_pcmIO(file_path)
    wav_buffer = pipeline.denoise_audioIO(wav_buffer)
    wav_buffer = pipeline.apply_vad(wav_buffer)
    print(f"Pré-processamento concluído. Tamanho final do buffer: {len(wav_buffer.getvalue())} bytes")
    
    
    # --- 5. Diarização com Observação de Progresso ---
    print("\n--- Diarização de Fala (Pyannote) ---")
    if hf_token:
        # 1. Carrega a função de diarização (e o pipeline global, se ainda não estiver carregado)
        # NOTA: O pipeline global não é retornado, mas é acessado via closure.
        diarize_io_function = pipeline.get_diarization_function(hf_token)
        
        print("Iniciando diarização com barra de progresso...")
        
        try:
            # 2. CHAMA A FUNÇÃO. O ProgressHook é ATIVADO INTERNAMENTE.
            # A função retorna os segmentos e o DEVICE.
            segments_list, device_used = diarize_io_function(wav_buffer)
            
            # 3. Recalcula o tempo total para o dicionário final
            wav_buffer.seek(0)
            waveform, sample_rate = torchaudio.load(wav_buffer)
            total_time = len(waveform[0]) / sample_rate 
            
            segments = {
                "segments" : segments_list,
                "total_len" : total_time,
                "sample_rate": sample_rate,
                "device": str(device_used) # Adiciona o dispositivo usado
            }

        except Exception as e:
            print(f"ERRO durante a diarização: {e}")
            segments = {} 
            # ... (restante do salvamento e fim do script) ...
        print("\nSegmentação Concluída:")

        # salvar diarização como json
        # criar caminho
        output_path = diarizacao_output_dir.create_file_path(f"diarizacao_{file_name}", "pkl", overwrite=True)
        with open(output_path, "wb") as fh:
            pickle.dump(segments, fh)

    else:
        print("IGNORADO: Diarização requer o token HF que não foi encontrado.")
    
    # --- 6. Salvamento Temporário (Para Debug) ---
    # ... (O código de salvamento do TempDirManager foi omitido para focar no hook, mas deve ser mantido) ...
    
    print("\n--- Fim do Processamento ---")
