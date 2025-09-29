from src.download_files import download_from_pac, pac_files
from src.process.pdf_to_tex import ocr_tesseract, extract_text_from_pdf
from pathlib import Path
from configPy import Config
import time


pacs = list(pac_files.get_files_by_porcent_url(pac_files.DotValue.DOT1))


package = download_from_pac(pacs[0], use_temp=False)

print(package.root_dir)

# amostra de arquivo

file = package.get_files()["ata"][0]
print(file)


# Diretório base para resultados de teste
output_dir = Config.get_dir_output()
ocr_test_dir = output_dir.create_dir("ocr_test_configs")

# Configurações de teste apenas em português: (descrição, dpi, psm)
ocr_configs = [
    ("fast_psm3_1", 200, 3),   # máxima qualidade, dpi alto, PSM 3
    ("fast_psm3_2", 300, 3),
    ("fast_psm3_3", 500, 3)
#    ("high_quality", 400, 3),  # alta qualidade
#    ("medium_quality", 300, 3),
#    ("fast", 200, 6),          # rápido
#    ("very_fast", 150, 6),     # muito rápido, menor dpi, PSM 6
]

# Amostra de arquivo PDF
file_path = Path(package.get_files()["ata"][0])

for desc, dpi, psm in ocr_configs:
    # Cria diretório específico para essa configuração
    config_dir = ocr_test_dir.create_dir(desc)

    # Arquivo que vai armazenar as configurações e tempo
    log_file = config_dir.create_file_path("config_and_time", "txt", overwrite=True)

    start_time = time.time()

    # Executa OCR com os parâmetros específicos
    ocr_tesseract(
        file_path,
        output=config_dir,
        dpi=dpi,
        workers=10,       # você pode variar também o número de threads
        lang="por",
        psm=psm
    )

    elapsed = time.time() - start_time

    # Salva log com parâmetros e tempo
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Descrição: {desc}\n")
        f.write(f"DPI: {dpi}\n")
        f.write(f"Idioma: por\n")
        f.write(f"PSM: {psm}\n")
        f.write(f"Tempo de execução (s): {elapsed:.2f}\n")

    print(f"[{desc}] OCR concluído em {elapsed:.2f}s")
