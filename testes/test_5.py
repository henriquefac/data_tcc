from src.download_files import pac_files, download_from_pac
from src.process.audio_to_tex import pipeline
from configPy import Config, EnvManager, TempDirManager
from json import dumps
import torch
import io
import torchaudio  # <--- Adicione esta linha
from pyannote.audio.pipelines.utils.hook import ProgressHook 
# --- 1. Configuração e Checagem de Hardware ---
print("--- Configuração de Hardware ---")
print(f"CUDA disponível: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Dispositivo GPU: {torch.cuda.get_device_name(0)}")
else:
    print("Usando CPU.")

# --- 2. Gerenciamento de Ambiente e Tokens ---
print("\n--- Gerenciamento de Ambiente ---")
envMan = EnvManager() 
try:
    hf_token = envMan.get_hugging_face_token()
    print("Token Hugging Face carregado.")
except EnvironmentError as e:
    print(f"ERRO: {e}. O processo de diarização PODE FALHAR.")
    hf_token = None 

# --- 3. Download e Arquivo ---
print("\n--- Download de Arquivo ---")
pac = pac_files.get_files_by_year_link(1)
package = download_from_pac(pac, 5, use_temp=True) 

try:
    file_path = package.get_files()["audio"][1]
    print(f"Arquivo de áudio selecionado: {file_path.name}")
except IndexError:
    print("ERRO: Não foi possível encontrar o arquivo de áudio na posição [1].")
    exit()

# --- 4. Pipeline de Pré-Processamento ---
print("\n--- Pré-Processamento de Áudio ---")
# O objeto final após o pré-processamento é necessário para a diarização
wav_buffer: io.BytesIO = pipeline.webm_to_pcmIO(file_path)
wav_buffer = pipeline.denoise_audioIO(wav_buffer)
wav_buffer = pipeline.apply_vad(wav_buffer)
print(f"Pré-processamento concluído. Tamanho final do buffer: {len(wav_buffer.getvalue())} bytes")


# --- 5. Diarização com Observação de Progresso ---
print("\n--- Diarização de Fala (Pyannote) ---")

if hf_token:
    diarize_io_function = pipeline.get_diarization_function(hf_token)
    
    print("Iniciando diarização com barra de progresso...")
    
    # O pipeline interno precisa ser chamado com o hook
    
    # Para fazer o ProgressHook funcionar, precisamos que a função diarization_io
    # (retornada por get_diarization_function) aceite o 'hook' como argumento.
    # No entanto, se ela não aceita, o uso mais simples é diretamente na chamada do pipeline:
    
    # **AVISO:** Como o pipeline em pyannote só pode ser chamado com 'hook' se o pipeline
    # interno for exposto, a forma mais robusta é adaptar a chamada aqui:
    
    try:
        # Carrega o pipeline GLOBALMENTE (se já não estiver carregado)
        diarization_pipeline = diarize_io_function.__closure__[0].cell_contents if diarize_io_function.__closure__ else None
        
        if diarization_pipeline is None:
            # Se a função não expôs o pipeline (caso o código original tenha sido alterado)
            # Faremos a chamada sem o hook, mas com aviso.
            print("AVISO: Não foi possível acessar o pipeline interno. Rodando sem ProgressHook.")
            segments = diarize_io_function(wav_buffer)
        else:
            # 5.1 OTIMIZAÇÃO: Carrega o waveform para a memória
            wav_buffer.seek(0)
            waveform, sample_rate = torchaudio.load(wav_buffer)
            waveform = waveform.to(diarization_pipeline.device)

            # 5.2 CHAMADA COM HOOK: Envolve a execução do pipeline no ProgressHook
            with ProgressHook() as hook:
                output = diarization_pipeline(
                    {"waveform": waveform, "sample_rate": sample_rate},
                    hook=hook
                )
            
            # 5.3 Processa o resultado do output do pipeline
            segments = []
            for segment, _, speaker in output.itertracks(yield_label=True):
                segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "speaker": speaker
                })
    
    except Exception as e:
        print(f"ERRO durante a diarização: {e}")
        segments = []

    print("\nSegmentação Concluída:")
    print(dumps(segments, indent=4))
else:
    print("IGNORADO: Diarização requer o token HF que não foi encontrado.")

# --- 6. Salvamento Temporário (Para Debug) ---
# ... (O código de salvamento do TempDirManager foi omitido para focar no hook, mas deve ser mantido) ...

print("\n--- Fim do Processamento ---")
input("Pressione Enter para finalizar o script.")
