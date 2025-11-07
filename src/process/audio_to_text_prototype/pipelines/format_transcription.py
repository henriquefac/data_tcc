from typing import List, Dict, Any


def format_time(seconds):
    milis = int((seconds - int(seconds))*1000)
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}.{milis:03}"

def format_transcription_output(transcription_segments: List[Dict[str, Any]]) -> str:
    """
    Formata a lista de segmentos de transcrição em uma string legível e estruturada

    Formato da saída:
    [00:00:05.200 - 00:00:12.800] Speaker 0: ....
    ....
    [ ... ] Speaker n: ....

    """

    formatted_text = []

    for segment in transcription_segments:
        start_time_str = format_time(segment["start"])
        end_time_str = format_time(segment["end"])
        speaker_label = segment["speaker"]
        text_content = segment["text"].strip()
        
        line = f"[{start_time_str} - {end_time_str}] {speaker_label}: {text_content}"
        formatted_text.append(line)

    return "\n".join(formatted_text)


