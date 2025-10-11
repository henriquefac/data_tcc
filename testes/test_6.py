# analaizar distribuição das falas feitas pela diarização
from configPy import Config
import pickle
import matplotlib.pyplot as plt
from typing import Dict, Any, List

# pasta para outputs de gráficos



# --- 1. CONFIGURAÇÃO E CARREGAMENTO DE DADOS ---

# Acessa o Singleton da Config e o diretório onde o pickle foi salvo
try:
    files_dir = Config.get_dir_files()
    # Usando o nome corrigido da pasta de saída
    diarizacao_data_dir = files_dir["diarizacao_data"] 
    
    # buscar diretórios 
    diarizacao_target = next(diarizacao_data_dir.iter_dirs())
    # Output para os gráficos

    output_graph_dir = diarizacao_target.create_dir("graficos")

except Exception as e:
    print(f"ERRO DE CONFIGURAÇÃO: Verifique a inicialização de ConfigPy. {e}")
    exit()

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

# os registros para plotagem serão:
# tempo do end(n) e start(n+1) para (respectivamente) dif(n) e dif(n) (duplicado)

# primeiro, apenas para um falante
# buscar falante com maior registro de segmentos

speakers = list(seg_by_speaker.keys())
speakers.sort(key=lambda x: len(seg_by_speaker[x]), reverse=True)

speaker = speakers[0]


# criar eixo_x e eixo_y

eixo_x = []
eixo_y = []

dict_start_end = star_end_by_speaker[speaker]
start = dict_start_end["start"]
end = dict_start_end["end"]

end = end[:-1]
start = start[1:]

# dif
dif = diff_pause_by_speaker[speaker]

for i, (end_n, start_n_1) in enumerate(zip(end, start)):
    eixo_x.append(end_n)
    eixo_y.append(dif[i])

    eixo_x.append(start_n_1)
    eixo_y.append(dif[i])


# saída do gráfico gerado

output_grafico = output_graph_dir.create_file_path("output_test_line", "png", overwrite=True)

# grafico de linha
plt.figure(figsize=(12,5))
plt.plot(eixo_x, eixo_y, drawstyle='steps-post', marker='o'
         , linestyle='-', markersize = 4, label=f"Pausa de {speaker}")

plt.title(f"Distribuição das pausas intra-falante ao longo do áudio ({speaker})")
plt.xlabel("Tempo do áudio (Segundos)")
plt.ylabel("Duração da Pausa (Segundos)")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend()


plt.savefig(output_grafico, dpi=300, bbox_inches='tight')


# histograma
output_grafico = output_graph_dir.create_file_path("output_test_hist", "png", overwrite=True)

plt.figure(figsize=(12,5))

plt.hist(
    x=dif,
    bins='auto',
    stacked=False,
    label=speaker,
    log=True
)

plt.title(f"Histograma da duração das pausas intra-falante ao longo do áudio ({speaker})")
plt.xlabel("Duração da pausa (segundos)")
plt.ylabel("Quantidade de pausas por categoria")
plt.legend()

plt.savefig(output_grafico, dpi=300, bbox_inches='tight')
