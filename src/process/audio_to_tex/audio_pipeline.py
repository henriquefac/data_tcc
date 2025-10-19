# Aqui deve ser encapsulado todo o processo necessário para realizar 
# o processamento de um arquivo de áudio

# A entrada da pipeline é um camiho para um arquivo de áudio

# 1 - Transformar o arquivo salvo localmente no hd em um buffer carregado
# na mememória RAM no formato wav (pcm_s16b), isso utiliza ffmpeg como um subprocess

# 2- A partir do buffer, o próximo passo é aplicar o modelo de denoise utilizando ffmpeg
# esse passo vai podificar o buffer original, reescrevendo ele. 

# 3 - Com o áudio limpo, é necessário aplicar o processo de voice activity detection (VAD)
# para identificar o momento em que alguém está falando.

# 4 - Agora com obuffer contendo apenas as falas e com os momentos de silêncio drasticamente reduzidos
# é aplicado um modelo (do huggingface) especializado no processo de diarização. O objeto gerado a partir dele 
# é um uma lista de dicionários contendo os segmentos das falas (start, end, speaker)

# 5 - A partir da lista de segmentos, será usado a biblioteca faster whisper, subdividindo o áudio a partir
# dos segmentos identificados e transcrevendo eles individualmente.


import io
from json import dumps
from src.process.audio_to_tex import parts
from configPy import EnvManager
import torchaudio
import torch

def process_single_audio(file_path_str: str)->str:
    
    try:
        hf_env = EnvManager.huggingface()
        
        hf_token = hf_env.HF_TOKEN
        hf_diarize_model = hf_env.HF_DIARIZE_MODEL


        # converter para wav
        wav_buffer: io.BytesIO = parts.webm_to_pcmIO(file_path_str)
        # limpar arquivo de áudio dos ruídos
        wav_buffer = parts.denoise_audioIO(wav_buffer)
        # aplicar voice activity detection
        wav_buffer = parts.apply_vad(wav_buffer)

        # Diarização
        segments_list = []
        if hf_token:
            diarize_io_function = parts.get_diarization_function(hf_token, hf_diarize_model)
            segments_list, _ = diarize_io_function(wav_buffer)
        else:
            raise EnvironmentError("Token de acesso ao modelo hugging face não foi encontrado")
        wav_buffer.seek(0)
        
        transcription = parts.transcribe_with_whisper(wav_buffer, segments_list)

        result = {
            "trasncription":transcription,
            'file_path':file_path_str,
            'status':'SUCCESS'
        }

        return dumps(result)

    except Exception as e:
        return dumps({
            "file_path":file_path_str,
            "status":'ERROR',
            "message":str(e),
            "text":None
        })

