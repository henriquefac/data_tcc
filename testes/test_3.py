from src.download_files import pac_files, download_from_pac
from src.process.audio_to_tex import get_webm_file_as_pcm


pac = pac_files.get_files_by_year_link(1)
package = download_from_pac(pac, 5, use_temp=True)


file = package.get_files()["audio"][0]

output_pcm, tempDir = get_webm_file_as_pcm.webm_to_pcm_16b(file)

print(output_pcm)

input()
