from src.download_files import pac_files, download_from_pac
from src.process.audio_to_text_prototype import parts
from configPy import Config
from json import dumps
import io
import numpy as np

import matplotlib.pyplot as plt

# Salvar resultado da transcriçã via whisper
files_dir = Config.get_dir_files()
grafico_dir = files_dir.create_dir("graficos").create_dir("segmentos")



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

output_dir = grafico_dir.create_dir(f"{file_name}_vad_graphs")

# diretório de output dda diarizção desse arquivo

# --- 4. parts de Pré-Processamento ---
print("\n--- Pré-Processamento de Áudio ---")
# O objeto final após o pré-processamento é necessário para a diarização
wav_buffer: io.BytesIO = parts.preprocess.preprocess_audio_ffmpeg(file_path)
wav_buffer = parts.remove_noise.denoise_audioIO_norm(wav_buffer)
print(f"Pré-processamento concluído. Tamanho final do buffer: {len(wav_buffer.getvalue())} bytes")


# segmentar com VAD


vad_segments = parts.voice_detection.get_vad_segments(wav_buffer)

print("Segmentação com VAD feito")
print("Extraindo medidas")

# tempo médio de cada segmento

vad_init = np.array([s["start"] for s in vad_segments])
vad_end = np.array([s["end"] for s in vad_segments])

mean = (vad_end - vad_init).sum() / len(vad_segments)


print("Média da duração dos segmentos")
print(f"Média: {mean}")
# tempo médio do intervalo entre segmentos

seg_interval = vad_init[1:] - vad_end[:-1]

mean_interval = seg_interval.sum() / len(seg_interval)

# ditribuição dos intervalos entre os segmentos

# distribuição por histograma

print("Criando gráficos para análise da distribuição dos segmentos")

print("Histograma da duração de cada segmento....")

durations = vad_end - vad_init  # já tem esses arrays

plt.figure(figsize=(12,5))
plt.hist(durations, bins=20, log=True, alpha=0.6)
plt.title("Histograma da duração dos segmentos de fala detectados pelo VAD")
plt.xlabel("Duração do segmento (s)")
plt.ylabel("Quantidade")
hist_dur_output = output_dir.create_file_path("histograma_duracao_segmentos","png",overwrite=True)
plt.savefig(hist_dur_output, dpi=300, bbox_inches="tight")
plt.close()
print(f"Histograma de duração das falas salvo em: {hist_dur_output}")


print("Histograma da duração dos intervalos entre segmentos....")

plt.figure(figsize=(12, 5))

plt.hist(seg_interval,
         bins=15,
         stacked=False,
         alpha=0.6,
         log=True)

plt.title("Histograma das pausas entre os segmentos feito pelo vad")
plt.xlabel("Duração das pausas")
plt.ylabel("Quantidade de pausas")
plt.legend()
hist_output = output_dir.create_file_path("histograma", "png", overwrite=True)
plt.savefig(hist_output, dpi=300, bbox_inches="tight")
plt.close()

print(f"Histograma de duração dos intervalos salvo em: {hist_output}")
# ------- (4) Detecção de segmentos muito curtos (potenciais falsos positivos) ---------

THRESH = 0.25  # 250 ms (pode ajustar)
short_segments = durations < THRESH
num_short = short_segments.sum()
pct_short = (num_short / len(durations)) * 100

print("\n--- Qualidade dos segmentos (checagem de curtos) ---")
print(f"Total de segmentos: {len(durations)}")
print(f"Segmentos curtos (<{THRESH*1000:.0f} ms): {num_short}  ({pct_short:.2f}%)")



# output
