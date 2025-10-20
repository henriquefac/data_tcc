import torch
import torchaudio
import io
from faster_whisper import WhisperModel
from .filter_segments import apply_segment_filters

DEVICE = "cuda"
SIZE = "large" 
whisper = WhisperModel(model_size_or_path=SIZE, device=DEVICE)

# --- Variável de Configuração de Precisão ---
DEFAULT_PROMPT = "Transcrição de uma reunião do plenário no Tribunal Regional Eleitoral"
# ---------------------------------------------


def transcribe_with_faster_whisper(audio_buffer:io.BytesIO, segments: list[dict], initial_prompt: str = DEFAULT_PROMPT):
    result = []
    audio_buffer.seek(0)
    
    # 1. Carrega a waveform COMPLETA UMA ÚNICA VEZ
    wave_form, sample_rate = torchaudio.load(audio_buffer)
    
    # 2. Move a waveform completa para a GPU
    wave_form = wave_form.to(DEVICE)
    
    # Garante que a waveform é mono (se não garantido antes)
    if wave_form.shape[0] > 1:
        wave_form = wave_form.mean(dim=0, keepdim=True)

    # 3. Itera sobre os segmentos e transcreve
    for seg in segments:
        start, end = float(seg["start"]), float(seg["end"])
        speaker = seg["speaker"]

        index_start = int(start * sample_rate)
        index_end = int(end * sample_rate)

        # CORTE DO TENSOR (ainda na GPU)
        segment_waveform = wave_form[:, index_start:index_end]
        
        # CONVERSÃO FINAL: Mova para CPU e converta para NumPy (entrada do Faster-Whisper)
        audio_array = segment_waveform.squeeze().cpu().numpy()
        
        # 4. TRANSCRIÇÃO (com filtros de decodificação para precisão)
        transcription, _ = whisper.transcribe(
            audio_array, 
            language="pt",
            initial_prompt=initial_prompt, 
            beam_size=5, 
            repetition_penalty=1.2,
            condition_on_previous_text=False 
        )

        text = " ".join([t.text for t in transcription])

        result.append({
            "start":start,
            "end":end,
            "speaker":speaker,
            "text": text.strip()
        })
        
        torch.cuda.empty_cache()

    return apply_segment_filters(result)
