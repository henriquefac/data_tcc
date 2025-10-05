from pyannote.audio.pipelines.utils.hook import ProgressHook



# Garanta que seu pipeline foi carregado aqui (exemplo)
# pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1", use_auth_token=token)

# 1. Abre o gerenciador de contexto ProgressHook
with ProgressHook() as hook:
    # 2. Chama o pipeline, passando o objeto 'hook' como argumento
    # O Pyannote agora sabe que deve reportar o progresso a este hook
    output = pipeline("audio.wav", hook=hook)
    
# 3. O 'hook' é automaticamente fechado ao sair do bloco 'with'
# O resultado da diarização está na variável 'output'
