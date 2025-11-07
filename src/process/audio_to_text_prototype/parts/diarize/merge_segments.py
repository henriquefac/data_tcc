# Função principal é recber uma lista dos segmentos indentificados:

# list[dict[str, int | str]]

# um segmento -> {"start": int, "end":int, "speaker":str}

# identificar threshold para juntar dois segmentos adjacentes
# que possuem o mesmo falor de "spekaer"
# threshold baseado na diferença de:

# seg(n+1)["start"] - seg(n)["end"]

# onde seg() representa uma função que recebe indice da lista de segmentos
# e retorna o objeto (dicionário) relativo ao index


import numpy as np
from skimage.filters import threshold_multiotsu

def get_threshold(segments_list: list[dict[str, float| str]]):
    # separar segmentos entre falantes

    segments_by_speaker = {}

    for segment in segments_list:
        speaker = str(segment["speaker"])
        segments_by_speaker.setdefault(speaker, []).append(segment)

    # para cada falante, calcular duração das pausas entre segmentos
    
    all_diffs = []

    for speaker, segs in segments_by_speaker.items():
        # Garantir ordenação temporal
        segs = sorted(segs, key=lambda s: s["start"])

        if len(segs) < 2:
            continue

        # Diferença vetorizada: start[n+1] - end[n]
        starts = np.array([s["start"] for s in segs[1:]])
        ends = np.array([s["end"] for s in segs[:-1]])
        diffs = starts - ends

        # Filtra valores negativos ou zero (sobreposições, erros de segmentação)
        all_diffs.extend(diffs[diffs > 0])    # com a lista feita, usar filtro de otsu para encontrar threshold dos segmentos
    diffs = np.sort(np.array(all_diffs))
    thresholds = threshold_multiotsu(diffs, classes=3)

    # com esses thresholds, separamos três classes pela duração das pausas
    # todas pausa abaixo do threshold 1 indica pausas feitas erroneamentes em uma fala contínua

    # as pausas que se encontram entr os thresholds 1 e 2 provavelmente são pauas feitas ao longo de falas
    # entre multiplas pessoas de fomra quase concorrente
    # acima do thrashold 2, são longas pausas, que indica que aquele falante deixou de falar por um lngo período

    return thresholds



def merge_dict(segment_left: dict[str, str | float], segment_right: dict[str, str | float]):

    return {
        "start":segment_left["start"],
        "end":segment_right["end"],
        "speaker":segment_left["speaker"]
    }


def merge_segments(segment_left: dict[str, str | float], segment_right: dict[str, str | float], threshold: float):
    
    same_segment = segment_left["speaker"] == segment_right["speaker"]
    gap = float(segment_right["start"]) - float(segment_left["end"])


    if same_segment and gap <= threshold and gap > 0:
        return merge_dict(segment_left, segment_right)

    if not same_segment and gap < -1:
        return merge_dict(segment_left, segment_right)
    
    return None




def apply_merge_aux(segments_list: list[dict[str, float | str]], threshold: float) -> list[dict[str, float | str]]:
    """
    Itera sobre a lista de segmentos e aplica fusões conforme o threshold.
    Retorna uma nova lista de segmentos unificados.
    """
    if not segments_list:
        return []

    segments_list = sorted(segments_list, key=lambda s: s["start"])
    merged = [segments_list[0]]

    for seg in segments_list[1:]:
        last = merged[-1]
        merged_seg = merge_segments(last, seg, threshold)

        if merged_seg:
            # Substitui o último segmento pelo novo unificado
            merged[-1] = merged_seg
        else:
            # Mantém o atual sem fusão
            merged.append(seg)

    return merged


def apply_merge(segments_list: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    """
    Detecta automaticamente o threshold (usando Otsu)
    e aplica o merge com base na pausa curta detectada.
    """
    thresholds = get_threshold(segments_list)
    short_pause_threshold = thresholds[0]  # primeira faixa (pausas curtas)
    return apply_merge_aux(segments_list, short_pause_threshold)
