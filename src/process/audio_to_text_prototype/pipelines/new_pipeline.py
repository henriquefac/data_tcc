from src.process.audio_to_text_prototype.parts import preprocess, remove_noise, diarize, whisper
from configPy import EnvManager
import torch
import io
from typing import List, Dict, Any

# ---------------------------------------------
def process_single_audio(file_path_str: str) -> List[Dict[str, Any]]:
    """
    Executa o pipeline completo: Pré-processamento, Denoise, Diarização e Transcrição.
    
    Args:
        file_path_str: Caminho para o arquivo de áudio ou vídeo de entrada (e.g., .webm, .mp4).
        
    Returns:
        Uma lista de dicionários com a transcrição segmentada e atribuída a falantes.
    """
    
    # 1. SETUP E CARREGAMENTO DE ENVS
    hf_env = EnvManager.huggingface()
    hf_token = hf_env.HF_TOKEN
    hf_diairize_model = hf_env.HF_DIARIZE_MODEL

    # 2. Inicialização da Função de Diarização
    try:
        # A função diarize.get_diarization_function agora retorna um closure.
        # Não precisamos mais do modelo 'large' na CPU, pois já está no 'whisper'
        diarize_fn = diarize.get_diarization_function(
            hf_token, 
            hf_diairize_model,
        )
    except Exception as e:
        raise EnvironmentError(f"Erro ao criar a função de diarização (Pyannote). Checar token.env: {e}")

    try:
        # 3. Pré-processamento (Conversão + Normalização Inicial)
        # Garante 16kHz, Mono e formato PCM, ideal para o pipeline.
        wav_buffer: io.BytesIO = preprocess.preprocess_audio_ffmpeg(
            file_path_str, 
            sample_rate=16000, 
            channels=1
        )

        # 4. Denoise e Loudnorm (Remoção de Ruído + Nivelamento Final)
        wav_buffer = remove_noise.denoise_audioIO_norm(wav_buffer)

        # 5. Diarização com Pyannote
        # O resultado é uma lista de segmentos com 'start', 'end', 'speaker'.
        segment_list, _ = diarize_fn(wav_buffer)

        # 6. Transcrição com Faster-Whisper (Otimizada para GPU)
        # Passa o buffer de áudio (o Whisper fará o seek(0) e o load)
        transcription = whisper.transcribe_with_faster_whisper(
            wav_buffer, 
            segment_list,
        )

        # 7. Limpeza de Recursos
        # Libera o Pyannote para uso futuro, mas evita OOM imediato.
        del wav_buffer 
        if torch.cuda.is_available():
             torch.cuda.empty_cache()

        return transcription

    except Exception as e:
        print(f"Erro fatal no processamento do arquivo {file_path_str}: {e}")
        
        # Garante limpeza mesmo em caso de erro
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        return []
