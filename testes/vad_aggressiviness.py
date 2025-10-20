from src.download_files import pac_files, download_from_pac
from src.process.audio_to_text_prototype import parts
from configPy import Config
import io
import torchaudio  # <--- Adicione esta linha


files_dir = Config.get_dir_files()
test_audio_dir = files_dir.create_dir("teste_audio_preprocess")


# aggressiviness
agg = 1

# --- 3. Download e Arquivo ---
print("\n--- Download de Arquivo ---")
pac = pac_files.get_files_by_year_link(1)
package = download_from_pac(pac, 5)

try:
    file_path = package.get_files()["audio"][1]
    print(f"Arquivo de áudio selecionado: {file_path.name}")
except IndexError:
    print("ERRO: Não foi possível encontrar o arquivo de áudio na posição [1].")
    exit()

file_name = file_path.stem

# diretório de output dda diarizção desse arquivo

# --- 4. parts de Pré-Processamento ---
print("\n--- Pré-Processamento de Áudio ---")
# O objeto final após o pré-processamento é necessário para a diarização
wav_buffer: io.BytesIO = parts.preprocess.preprocess_audio_ffmpeg(file_path)
wav_buffer = parts.remove_noise.denoise_audioIO_norm(wav_buffer)
wav_buffer = parts.voice_detection.apply_vad(wav_buffer, agg)
print(f"Pré-processamento concluído. Tamanho final do buffer: {len(wav_buffer.getvalue())} bytes")


output_path = test_audio_dir.create_file_path(f"{file_name}_preprocessed_denoise_vad_agg_{agg}", "wav", True)

parts.preprocess.save_wavIO(wav_buffer, output_path)
