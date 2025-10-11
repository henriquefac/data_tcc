import torch
import torchaudio
import io
from faster_whisper import WhisperModel


DEVICE, SIZE = ("cuda", "large") if torch.cuda.is_available() else ("cpu", "small")
whisper = WhisperModel(model_size_or_path=SIZE, device=DEVICE)



def transcribe_with_whisper(audio_buffer:io.BytesIO, segments: list[dict]):
    result = []

    audio_buffer.seek(0)
    
    segment_buffer = io.BytesIO()
    segment_buffer.seek(0)

    wave_form, sample_rate = torchaudio.load(audio_buffer)

    for seg in segments:
        start, end = float(seg["start"]), float(seg["end"])
        speaker = seg["speaker"]

        index_start = int(start * sample_rate)
        index_end = int(end * sample_rate)

        segment_waveform = wave_form[:, index_start:index_end]
        
        torchaudio.save(segment_buffer, segment_waveform.cpu(),sample_rate=sample_rate ,format="wav")
        segment_buffer.seek(0)

        transcription, _ = whisper.transcribe(segment_buffer, language="pt")

        text = " ".join([t.text for t in transcription])

        result.append({
            "start":start,
            "end":end,
            "speaker":speaker,
            "text": text.strip()
        })

        segment_buffer.truncate(0)
        segment_buffer.seek(0)

    return result
