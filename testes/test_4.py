from src.download_files import pac_files, download_from_pac
from src.process.audio_to_tex import pipeline
from configPy import Config, EnvManager, TempDirManager
from json import dumps
import torch

print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))


envMan = EnvManager()

hf_token = envMan.get_hugging_face_token()


pac = pac_files.get_files_by_year_link(1)
package = download_from_pac(pac, 5, use_temp=True)


file = package.get_files()["audio"][1]

print(file)

# Transformar arquivo em .wav
print("Lendo arquivo como wav em memória")
wav_buffer = pipeline.webm_to_pcmIO(file)
print(f"tamanho do buffer: {len(wav_buffer.getvalue())}")
print("Removendo interferência do áudio")
wav_buffer = pipeline.denoise_audioIO(wav_buffer)
print(f"tamanho do buffer: {len(wav_buffer.getvalue())}")
print("Realizando detecção de fala")
wav_buffer = pipeline.apply_vad(wav_buffer)
print(f"tamanho do buffer: {len(wav_buffer.getvalue())}")


diarization = pipeline.get_diarization_function(hf_token)

print("Realizar diarização")
segments = diarization(wav_buffer) 

print("Segmentação:")
print(dumps(segments, indent=4))

# criar path para salvar o resultado
file_dir = Config.get_dir_files()
tmp_dir = TempDirManager(file_dir)


output_path = tmp_dir.create_file_path("outputTMP", "wav")

pipeline.save_wavIO(wav_buffer, output_path)


input()
