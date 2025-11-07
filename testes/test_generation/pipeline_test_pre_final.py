from src.process.audio_to_text_prototype import pipelines
from src.download_files import pac_files, download_from_pac
import torch
from configPy import Config

from typing import List, Dict, Any

# --- CONFIGURAÇÃO DE SAÍDA ---
OUTPUT_SUFFIX = "_transcricao_final"
OUTPUT_FORMAT = "txt"
# -----------------------------

# Inicializa diretórios (assumindo que Config está configurado corretamente)
files_dir = Config.get_dir_files()
output_dir = Config.get_dir_output()
output_audio_dir = output_dir.create_dir("audio_testes")

def format_transcript_output(transcription_segments: List[Dict[str, Any]]) -> str:
    """
    Formata a lista de segmentos de transcrição em uma string legível e estruturada.
    
    Formato de Saída:
    [00:00:05.200 - 00:00:12.800] Speaker 0: Olá, sejam todos bem-vindos à nossa reunião semanal.
    [00:00:13.500 - 00:00:25.100] Speaker 1: Obrigado! Gostaria de começar com a pauta de hoje.
    """
    formatted_text = []

    def format_time(seconds):
        # Converte segundos para o formato HH:MM:SS.ms
        millis = int((seconds - int(seconds)) * 1000)
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}.{millis:03}"

    for segment in transcription_segments:
        start_time_str = format_time(segment["start"])
        end_time_str = format_time(segment["end"])
        speaker_label = segment["speaker"]
        text_content = segment["text"].strip()
        
        # Estrutura a linha: [Tempo Inicial - Tempo Final] Falante: Conteúdo
        line = f"[{start_time_str} - {end_time_str}] {speaker_label}: {text_content}"
        formatted_text.append(line)
    
    return "\n".join(formatted_text)


if __name__ == "__main__":
    

    print("--- Configurações de Hardware ---")
    print(f"CUDA disponível: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Dispositivo GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Usando CPU.")



    # 1. DOWNLOAD E SELEÇÃO DE ARQUIVO
    print("\n" + "="*50)
    print("--- 1. INICIANDO DOWNLOAD E SELEÇÃO DE ARQUIVO ---")
    print("="*50)

    try:
        # Tenta baixar o pacote do ano 1, índice 5 (valores de teste)
        pac = pac_files.get_files_by_year_link(1)
        package = download_from_pac(pac, 5)
        
        # Seleciona o segundo arquivo de áudio (índice 1) para processamento
        file_path = package.get_files()["audio"][1]
        file_name = file_path.stem
        
        print(f"Arquivo de áudio selecionado: {file_path.name}")
        
    except IndexError:
        print("ERRO: Não foi possível encontrar o arquivo de áudio na posição [1] ou o pacote está vazio.")
        exit(1)
    except Exception as e:
        print(f"ERRO durante o download ou seleção de arquivo: {e}")
        exit(1)

    # 2. PROCESSAMENTO DO PIPELINE
    print("\n" + "="*50)
    print(f"--- 2. REALIZANDO PROCESSAMENTO DO PIPELINE: {file_name} ---")
    print("="*50)
    
    try:
        # Chamada à função principal do pipeline
        transcription_data = pipelines.process_single_audio(str(file_path))

    except EnvironmentError as e:
        # Erro de ambiente, geralmente relacionado ao token Pyannote
        print(f"ERRO de configuração do Ambiente (Pyannote): {e}")
        exit(1)
    except Exception as e:
        # Erros gerais durante o processamento (ffmpeg, denoise, whisper)
        print(f"ERRO FATAL durante o processamento: {e}")
        exit(1)


    # 3. SAÍDA E SALVAMENTO DO RESULTADO
    print("\n" + "="*50)
    print("--- 3. SALVANDO TRANSCRIÇÃO FINAL ---")
    print("="*50)

    # Gera o nome do arquivo final com o sufixo e extensão
    file_final_name = output_audio_dir.create_file_path(
        f"{file_name}{OUTPUT_SUFFIX}", 
        OUTPUT_FORMAT, overwrite=True
    )

    # Formata os dados de transcrição em texto legível
    formatted_transcript = format_transcript_output(transcription_data)
    
    try:
        # Salva o resultado formatado
        with open(file_final_name, "w", encoding="utf-8") as file:
            file.write(formatted_transcript)
            
        print(f"Transcrição concluída e salva em: {file_final_name}")

    except IOError as e:
        print(f"ERRO ao salvar o arquivo: {e}")

    print("\n" + "="*50)
    print("--- FIM DO PROCESSAMENTO ---")
    print("="*50)
    input("Pressione Enter para finalizar o script ---") # Mantido comentado para execução automática
