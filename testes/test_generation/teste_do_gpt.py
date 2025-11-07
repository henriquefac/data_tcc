from src.process.audio_to_text_prototype import pipelines
from src.process.pdf_to_tex import extract_text_from_single_pdf
from src.download_files import pac_files, download_from_pac
from configPy import Config, DirManager
from pathlib import Path
import traceback

OUTPUT_FORMAT = "txt"

# --- Diretórios de saída ---
output_dir = Config.get_dir_output()
output_audio_dir = output_dir.create_dir("audio")
output_ata_dir = output_dir.create_dir("ata")

# --- Download dos arquivos PAC ---
print("Baixando arquivos de exemplo...")
pac = pac_files.get_files_by_year_url_link(1)
package = download_from_pac(pac, n_workers=5, use_temp=True)
all_files = package.get_files()

audio_files = all_files["audio"]
pdf_files = all_files["ata"]

print(f"Arquivos baixados: {len(pdf_files)} atas e {len(audio_files)} áudios.\n")

# -----------------------------------------------------------
# Funções de conversão isoladas
# -----------------------------------------------------------

def convert_ata_to_text(ata: Path, output_path: Path | None) -> str:
    """Extrai texto de uma ata PDF e retorna como string."""
    if output_path is None:
        return ""
    return extract_text_from_single_pdf(ata)

def convert_audio_to_text(audio: Path, output_path: Path | None) -> str:
    """Executa a pipeline de áudio completa (pré-processamento + Whisper + filtros)."""
    if output_path is None:
        return ""
    return pipelines.process_single_audio(str(audio))

# -----------------------------------------------------------
# Função principal de execução por par de arquivos
# -----------------------------------------------------------

def convert_tuple_files(ata: Path, audio: Path,
                        output_ata: DirManager, output_audio: DirManager):
    """
    Converte uma dupla (ata, áudio) e salva os resultados.
    """
    base_name = ata.stem

    print(f"\n[PROCESSANDO] {base_name}")

    try:
        output_ata_file = output_ata.create_file_path(name=base_name, suffix=OUTPUT_FORMAT, overwrite=False)
    except Exception:
        print(f"⚠️ Arquivo de ata '{base_name}' já existe — ignorando conversão.")
        output_ata_file = None

    try:
        output_audio_file = output_audio.create_file_path(name=base_name, suffix=OUTPUT_FORMAT, overwrite=False)
    except Exception:
        print(f"⚠️ Arquivo de áudio '{base_name}' já existe — ignorando conversão.")
        output_audio_file = None

    try:
        # --- ATA ---
        text_ata = convert_ata_to_text(ata, output_ata_file)
        if text_ata:
            with open(output_ata_file, "w", encoding="utf-8") as f:
                f.write(text_ata)
            print(f"✓ Ata convertida e salva em {output_ata_file.name}")
        else:
            print(f"⚠️ Ata vazia ou erro de extração: {ata.name}")

        # --- ÁUDIO ---
        text_audio = convert_audio_to_text(audio, output_audio_file)
        if text_audio:
            with open(output_audio_file, "w", encoding="utf-8") as f:
                f.write(text_audio)
            print(f"✓ Áudio convertido e salvo em {output_audio_file.name}")
        else:
            print(f"⚠️ Áudio retornou vazio: {audio.name}")

    except Exception as e:
        print(f"❌ Erro durante processamento de {base_name}: {e}")
        traceback.print_exc()


# -----------------------------------------------------------
# Execução em lote
# -----------------------------------------------------------

# Estratégia simples: parear por índice (assumindo ordem igual no PAC)
total_pairs = min(len(pdf_files), len(audio_files))
print(f"Executando conversão para {total_pairs} pares de arquivos...\n")

for i in range(total_pairs):
    ata = pdf_files[i]
    audio = audio_files[i]
    convert_tuple_files(ata, audio, output_ata_dir, output_audio_dir)

print("\n✅ Conversão finalizada com sucesso!")
