from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import torchaudio
import io
import torch

pipeline: Pipeline | None = None
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_diarization_function(token: str, repo: str = "pyannote/speaker-diarization-community-1"):
    """
    Retorna uma função configurada para rodar diarização de áudio diretamente de um buffer (BytesIO).
    """
    global pipeline

    if pipeline is None:
        print(f"Carregando modelo Pyannote para o dispositivo: {DEVICE}")
        pipeline = Pipeline.from_pretrained(repo, token=token)
        pipeline.to(DEVICE)

    def diarization_io(audio_buffer: io.BytesIO):
        """
        Executa a diarização diretamente no buffer de memória.
        Retorna a transcrição temporal de falantes.
        """
        audio_buffer.seek(0)

        # 1. Carrega o áudio diretamente do buffer
        try:
            waveform, sample_rate = torchaudio.load(audio_buffer)
        except Exception as e:
            raise IOError(f"Falha ao carregar áudio do buffer: {e}")

        waveform = waveform.to(DEVICE)

        # 2. Executa a diarização com barra de progresso
        print("Iniciando diarização...")
        with ProgressHook() as hook:
            diarization_result = pipeline(
                {"waveform": waveform, "sample_rate": sample_rate},
                hook=hook
            )

        # 3. Extrai os segmentos de forma compatível com versões antigas e novas
        segments = []
        for turn, speaker in diarization_result.speaker_diarization:
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
        return segments, DEVICE

    return diarization_io
