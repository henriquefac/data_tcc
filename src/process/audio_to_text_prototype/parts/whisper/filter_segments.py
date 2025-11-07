from typing import List, Dict, Any

# Lista de palavras-chave comuns que indicam que o Whisper transcreveu uma legenda/cabeçalho
# Estas palavras são frequentemente transcritas em áudios sem fala ou de baixa qualidade.
ARTIFACT_KEYWORDS = [
    "legendas", "legenda", "transcrição", "transcricao", 
    "música", "silêncio", "música alta", "[música]"
]


# vicio delinguaem identificado
ADDICT = [
"do Tribunal Eleitoral."
]

def apply_segment_filters(transcription_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aplica filtros de qualidade semântica e textual aos segmentos transcritos.

    Filtros aplicados:
    1. Comprimento Mínimo: Ignora segmentos com menos de 15 caracteres.
    2. Artefatos de Transcrição: Ignora segmentos que contenham palavras-chave
       como "Legenda" ou "Transcrição" sem pontuação de frase.
    3. Confiabilidade (Inferida): Ignora segmentos com texto que parece ser apenas ruído.

    Args:
        transcription_segments: Lista de segmentos após a transcrição do Whisper.

    Returns:
        Lista filtrada de segmentos de transcrição.
    """
    filtered_segments = []

    for segment in transcription_segments:
        text: str = segment["text"].strip()
        
        # Se a transcrição falhou ou retornou string vazia, pula.
        if not text:
            continue

        # 1. Filtro de Comprimento Mínimo (Min length filter)
        # O padrão é que textos muito curtos (ex: "uh" ou ruído) sejam descartados.
        MIN_CHAR_LENGTH = 15
        if len(text) < MIN_CHAR_LENGTH:
            # print(f"DEBUG: Pulando por ser muito curto ({len(text)}): '{text[:15]}...'")
            continue

        if text in ADDICT:
           continue

        # 2. Filtro de Artefatos de Transcrição e Confiabilidade Baixa (Keywords filter)
        # Verifica se o texto contém palavras-chave indesejadas E não parece ser uma frase completa.
        is_artifact = False
        
        # Converte para minúsculas e remove pontuação para análise simples
        clean_text = text.lower().replace('.', '').replace(',', '').replace(':', '').strip()
        
        for keyword in ARTIFACT_KEYWORDS:
            if keyword in clean_text:
                # Se contém a palavra-chave E o texto não termina em um ponto final válido, 
                # assumimos que é um artefato de transcrição ou de baixa confiabilidade.
                # Exemplo: "Legenda Transcrição" é ruim. "Isso é uma transcrição." pode ser aceito.
                if not text.endswith(('.', '?', '!')):
                    is_artifact = True
                    # print(f"DEBUG: Pulando por artefato: '{text[:20]}...'")
                    break
        
        if is_artifact:
            continue
            
        # 3. Filtro de Confiabilidade Baixa (Ruído)
        # O Whisper pode transcrever ruído como uma repetição de vogais ou sons aleatórios.
        
        # Filtro: Se o texto contiver muitas repetições do mesmo caractere (sem ser vogal/consoante), ignora.
        if "..." in text or "ah" * 3 in clean_text or "eh" * 3 in clean_text:
             # print(f"DEBUG: Pulando por ruído inferido: '{text[:20]}...'")
             continue

        # Se passou por todos os filtros, é um segmento válido
        filtered_segments.append(segment)

    return filtered_segments
