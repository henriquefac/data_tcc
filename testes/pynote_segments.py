from src.download_files import pac_files, download_from_pac
from src.process.audio_to_text_prototype import parts
from configPy import Config, EnvManager
import io
import numpy as np

import torch
import torchaudio

import matplotlib.pyplot as plt

# Salvar resultado da transcriçã via whisper
files_dir = Config.get_dir_files()
grafico_dir = files_dir.create_dir("graficos").create_dir("segmentos")

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
hf_env = envMan.huggingface()
try:
    hf_token = hf_env.HF_TOKEN
    hf_diarize_model = hf_env.HF_DIARIZE_MODEL
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

output_dir = grafico_dir.create_dir(f"{file_name}_pynote_graphs")

# diretório de output dda diarizção desse arquivo

# --- 4. parts de Pré-Processamento ---
print("\n--- Pré-Processamento de Áudio ---")
# O objeto final após o pré-processamento é necessário para a diarização
wav_buffer: io.BytesIO = parts.preprocess.preprocess_audio_ffmpeg(file_path)
wav_buffer = parts.remove_noise.denoise_audioIO_norm(wav_buffer)
print(f"Pré-processamento concluído. Tamanho final do buffer: {len(wav_buffer.getvalue())} bytes")

# --- 5. Diarização com Observação de Progresso ---
print("\n--- Diarização de Fala (Pyannote) ---")
if hf_token:
    # 1. Carrega a função de diarização (e o parts global, se ainda não estiver carregado)
    # NOTA: O parts global não é retornado, mas é acessado via closure.
    diarize_io_function = parts.diarize.get_diarization_function(hf_token)
    
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
        segments_list = [] 
        # ... (restante do salvamento e fim do script) ...
    print("\nSegmentação Concluída:")
    print(f"Quantidade de segmentos: {len(segments_list)}")

    # salvar diarização como json
    # criar caminho

else:
    raise ValueError("IGNORADO: Diarização requer o token HF que não foi encontrado.")


seg_start = np.array([s["start"] for s in segments_list])
seg_end   = np.array([s["end"] for s in segments_list])

# --- (1) Média de duração dos segmentos ---
dur = seg_end - seg_start
mean_dur = dur.mean()
print(f"Média duração dos segmentos (s): {mean_dur:.3f}")

# --- (2) Média dos intervalos entre segmentos ---
if len(seg_start) > 1:
    seg_interval = seg_start[1:] - seg_end[:-1]
    mean_interval = seg_interval.mean()
    print(f"Média das pausas (s): {mean_interval:.3f}")
else:
    seg_interval = np.array([])
    print("Só 1 segmento — sem intervalos")

# --- (3) Histograma das pausas ---
plt.figure(figsize=(10,4))
plt.hist(seg_interval, bins=20, log=True)
plt.title("Pausas entre segmentos (Pyannote)")
plt.xlabel("Duração (s)")
plt.ylabel("Frequência")
hist_pause_path = output_dir.create_file_path("pausas_pyannote","png",overwrite=True)
plt.savefig(hist_pause_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"Histograma pausas salvo em {hist_pause_path}")

# --- (4) Histograma duração dos segmentos ---

plt.figure(figsize=(10,4))
plt.hist(dur, bins=20, log=True)
plt.title("Duração dos segmentos (Pyannote)")
plt.xlabel("Duração (s)")
plt.ylabel("Frequência")
hist_dur_path = output_dir.create_file_path("duracao_pyannote","png",overwrite=True)
plt.savefig(hist_dur_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"Histograma durações salvo em {hist_dur_path}")

# --- (5) Segmentos muito curtos (benchmark qualitativo) ---
TH = 0.25  # 250ms
short = (dur < TH).sum()
print(f"Segmentos curtos (<{TH}s): {short}  ({100*short/len(dur):.2f}%)")
