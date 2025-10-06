import webrtcvad
import wave
import io



def apply_vad(audio_buffer:io.BytesIO, aggressiveness:int = 1)->io.BytesIO:
    audio_buffer.seek(0)

    with wave.open(audio_buffer, "rb") as wave_file:
        sample_rate = wave_file.getframerate()
        pcm_data = wave_file.readframes(wave_file.getnframes())
    

    vad = webrtcvad.Vad(aggressiveness) # detector de fala VAD
    frame_ms = 30 # pode ser 10, 20 ou 30
    frame_bytes = int(sample_rate * 2 * frame_ms / 1000) 
    # sampe por milesecond * 2 (quantidade de bytes por sample) * frames por milesegundo, depois passe para segundo
    frames = [pcm_data[i:i+frame_bytes] for i in range(0, len(pcm_data), frame_bytes)]
    
    # verificar a cada frame (bytes agrupados) se possui fala
    voiced_frames = [f for f in frames if len(f) == frame_bytes and vad.is_speech(f,sample_rate)]

    filtered = b"".join(voiced_frames)

    audio_buffer.seek(0)
    audio_buffer.truncate(0)

    with wave.open(audio_buffer, "wb") as wf_out:

        # informações do cabeçalho do arquivo
        wf_out.setnchannels(1) # aepnas um canal (mono)
        wf_out.setsampwidth(2) # dois bytes or amostra
        wf_out.setframerate(sample_rate) # taxa de amostragem

        # audio filtrado
        wf_out.writeframes(filtered)
    
    audio_buffer.seek(0) # retornando o ponteiro para o início para futuras leituras
    return audio_buffer
