import webrtcvad
import io
import torchaudio

def get_vad_segments(audio_buffer: io.BytesIO, aggressivenes: int = 2, frame_ms: int = 10):
    audio_buffer.seek(0)

    waveform, sr = torchaudio.load(audio_buffer)
    waveform_int16 = (waveform * 32768).short()
    waveform_bytes = waveform_int16.numpy().tobytes()
    vad = webrtcvad.Vad(aggressivenes)


    frame_bytes = int(sr * 2 * frame_ms / 1000)
    frames = [waveform_bytes[i:i+frame_bytes] for i in range(0, len(waveform_bytes), frame_bytes)]
    
    segments = []
    current_start = None
    for i, frame in enumerate(frames):
        if len(frame) < frame_bytes:
            continue
        is_speech = vad.is_speech(frame, sr)
        t_start = i * frame_ms / 1000
        t_end = (i+1) * frame_ms / 1000
        
        if is_speech and current_start is None:
            current_start = t_start
        elif not is_speech and current_start is not None:
            segments.append({"start": current_start, "end": t_start})
            current_start = None
    if current_start is not None:
        segments.append({"start": current_start, "end": len(waveform[0])/sr})
    
    return segments
