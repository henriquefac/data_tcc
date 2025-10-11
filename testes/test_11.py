
# analaizar distribuição das falas feitas pela diarização
from configPy import Config
import pickle
import matplotlib.pyplot as plt
from typing import Dict, Any, List
import numpy as np
from skimage.filters import threshold_multiotsu  
# --- 1. CONFIGURAÇÃO E CARREGAMENTO DE DADOS ---

# Acessa o Singleton da Config e o diretório onde o pickle foi salvo
try:
    files_dir = Config.get_dir_files()
    # Usando o nome corrigido da pasta de saída
    diarizacao_data_dir = files_dir["diarizacao_data"] 
    
    # buscar diretórios 
    diarizacao_dirs = list(diarizacao_data_dir.iter_dirs())


except Exception as e:
    print(f"ERRO DE CONFIGURAÇÃO: Verifique a inicialização de ConfigPy. {e}")
    exit()


for diarizacao_target in diarizacao_dirs:
    output_graph_dir = diarizacao_target.create_dir("grafico")
    # Busca o primeiro arquivo .pkl
    try:
        file = next(diarizacao_target.iter_files())
        with open(file, "rb") as fh:
            diarizacao: Dict[str, Any] = pickle.load(fh)
    
        segments: List[Dict[str, float | str]] = diarizacao.get("segments", [])
        total_len: float = diarizacao.get("total_len", 0.0)
        
        print(f"Arquivo de diarização carregado: {file.name}")
        print(f"Duração total do áudio: {total_len:.2f}s")
    except Exception as e:
        print(f"ERRO ao carregar o arquivo pickle: {e}")
        exit()

    # buscar informações sobre a pausa entre segmentos para cada falante
    # priemrio, separar segmentos por falante

    # --- AGRUPAMENTO -----

    seg_by_speaker = {}

    for seg in segments:
        speaker = seg["speaker"]
        seg_by_speaker.setdefault(speaker, []).append(seg) # Usa .append() para adicionar o dicionário# agora, cada segmentos está associado ao seu respectivo falante
    # a partir disso, para cada falante, separar os tempos de início 
    # do segmento do tempo de fim do segmento

    star_end_by_speaker = {}

    # Extrair os tempos de início e fim
    for speaker, list_segment in seg_by_speaker.items(): 
        start = [seg["start"] for seg in list_segment]
        end = [seg["end"] for seg in list_segment]

        star_end_by_speaker[speaker] = {"start": start, "end": end}

        
    # Com os tempos de começo e fim separados em listas, ordenados pela 
    # ordem dos segmentos, é possível calcular o tempo de pausa entre os segmentos

    # --- CALCULAR DURAÇÂO DAS PAUSAS POR FALANTE ---
    diff_pause_by_speaker = {}
    avg_pause_by_speaker = {}

    for speaker, dict_start_end in star_end_by_speaker.items():
        start = dict_start_end["start"]
        end = dict_start_end["end"]

        if len(start) < 2:
            diff_pause_by_speaker[speaker] = []
            avg_pause_by_speaker[speaker] = 0.0

        # rempver ultimo registro de end
        end = end[:-1]
        # remover primeiro registro de start
        start = start[1:]

        # ideia: star(n+1) - end(n) = dif(n)

        dif = [start[i] - end[i]for i in range(len(start))]


        diff_pause_by_speaker[speaker] = dif
        avg_pause_by_speaker[speaker] = sum(dif) / len(dif) if dif else 0.0

    # para cada lista, relacionar m umgráfico quanto ao tempo do áudio
    # Eixo x - do segundo 0 até o segundo máximo de duração do wav
    # Eixo y - valor da diferença
    
    speakers = list(seg_by_speaker.keys())
    speakers.sort(key=lambda x: len(seg_by_speaker[x]), reverse=True)
       # os registros para plotagem serão:
    # tempo do end(n) e start(n+1) para (respectivamente) dif(n) e dif(n) (duplicado)
    # --- HISTOGRAMA (TODOS OS FALANTES) ---
    plt.figure(figsize=(12, 5))
    
    # Acumula todas as pausas em uma lista só (para análise combinada)
    all_dif = []
    for speaker in speakers:
        dif = diff_pause_by_speaker[speaker]
        if dif:
            all_dif.extend(dif)
    
    all_dif.sort(reverse=True)



    all_dif = np.array(all_dif)
    all_dif = all_dif[all_dif > 0]  # remove zeros e valores negativos se houver
    all_dif = np.sort(all_dif)
    
    indexes = np.arange(len(all_dif))
    try:
        thresholds = threshold_multiotsu(all_dif, classes=3)
        print(f"📏 Thresholds (Multi-Otsu): {thresholds}")
    except Exception as e:
        print(f"⚠️ Falha ao calcular Multi-Otsu: {e}")
        thresholds = []
    
    # --- Plotar histograma com faixas ---
    plt.figure(figsize=(10, 6))
    plt.hist(all_dif, bins=60, color="lightblue", edgecolor="black", alpha=0.7)
    plt.title("Distribuição das pausas entre segmentos (Multi-Otsu)")
    plt.xlabel("Duração da pausa (s)")
    plt.ylabel("Frequência")
    plt.grid(alpha=0.3)
    
    colors = ["green", "orange", "red"]
    labels = ["Pausa curta (fala contínua)", "Pausa média (troca rápida)", "Pausa longa (silêncio)"]
    
    for i, t in enumerate(thresholds):
        plt.axvline(t, color=colors[i], linestyle="--", linewidth=2,
                    label=f"Threshold {i+1} ≈ {t:.3f}s")
    
    plt.legend()
    plt.tight_layout()
        # --- Salvar gráfico ---
    output_path = output_graph_dir.create_file_path("grafico_pausas_otsu", "png", overwrite=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
