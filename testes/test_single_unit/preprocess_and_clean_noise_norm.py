from src.process.audio_to_text_prototype.parts import remove_noise, preprocess
from src.download_files import pac_files, download_from_pac
from configPy import Config
import io

# Salvar resultados da transcrição via whisper
files_dir = Config.get_dir_files()
test_audio_dir = files_dir.create_dir("teste_audio_preprocess")


# --- 3. Donwload de arquivos ---
print("\n--- Download de Arquivo ---")

pac = pac_files.get_files_by_year_link(1)
package = download_from_pac(pac, 5)
print("\n---------------------------")
try:
    file_path = package.get_files()["audio"][1]
    print(f"Arquivo de áudio selecionado: {file_path.name}")
except IndexError:
    print("ERRO: não foi possível encontrar o arquivo de áudio na possição [1].")
    exit()

# nome do arquivo para salvar transcrição
file_name = file_path.stem

processed_audio:io.BytesIO = preprocess.preprocess_audio_ffmpeg(file_path)

# remover ruídos
clean_noise_audio:io.BytesIO = remove_noise.denoise_audioIO_norm(processed_audio)


# arquivo de saída

output_path = test_audio_dir.create_file_path(f"{file_name}_preprocessed_denoissed_deepfilter", "wav")


preprocess.save_wavIO(clean_noise_audio, output_path)

print(f"Áudio pré-processado salvo em: {output_path}")
