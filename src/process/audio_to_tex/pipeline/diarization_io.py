from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import torchaudio
import io
import torch

pipeline: Pipeline | None = None
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# criar função para unir dois segmentos que são vizinhos
# que possuem o mesmo falante
# e possuem uma diferença de tempo muito pequena
def unify_segments(segment_1:dict[str, str | int], segment_2: dict[str, str | int])->dict[str, str | int]:
    new_seg = {}
    new_seg["start"] = segment_1["start"]
    new_seg["end"] = segment_2["end"]
    new_seg["speaker"] = segment_2["speaker"]
    
    return new_seg



def get_diarization_function(token: str, repo: str = "pyannote/speaker-diarization-community-1"):
    global pipeline

    if pipeline is None:
        print(f"Carregando modelo Pyannote para o dispositivo: {DEVICE}")
        pipeline = Pipeline.from_pretrained(repo, token=token)
        pipeline.to(DEVICE)

    def diarization_io(audio_buffer: io.BytesIO):
        audio_buffer.seek(0)

        try:
            waveform, sample_rate = torchaudio.load(audio_buffer)
        except Exception as e:
            raise IOError(f"Falha ao carregar áudio do buffer: {e}")

        waveform = waveform.to(DEVICE)

        print("Iniciando diarização...")
        with ProgressHook() as hook:
            diarization_result = pipeline(
                {"waveform": waveform, "sample_rate": sample_rate},
                hook=hook
            )

        segments = []
        try:
            for turn, speaker in diarization_result.speaker_diarization:
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
        except AttributeError:
            for label in diarization_result.labels():
                for turn in diarization_result.get_timeline(label):
                    segments.append({
                        "start": turn.start,
                        "end": turn.end,
                        "speaker": label
                    })

        return segments

    return diarization_io
