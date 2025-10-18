# Aqui deve ser encapsulado todo o processo necessário para realizar 
# o processamento de um arquivo de áudio

# A entrada da pipeline é um camiho para um arquivo de áudio

# 1 - Transformar o arquivo salvo localmente no hd em um buffer carregado
# na mememória RAM no formato wav (pcm_s16b), isso utiliza ffmpeg como um subprocess

# 2- A partir do buffer, o próximo passo é aplicar o modelo de denoise utilizando ffmpeg
# esse passo vai podificar o buffer original, reescrevendo ele. 

# 3 - Com o áudio limpo, é necessário aplicar o processo de voice activity detection (VAD)
# para identificar o momento em que alguém está falando.

# 4 - Agora com obuffer contendo apenas as falas e com os momentos de silêncio drasticamente reduzidos
# é aplicado um modelo (do huggingface) especializado no processo de diarização. O objeto gerado a partir dele 
# é um uma lista de dicionários contendo os segmentos das falas (start, end, speaker)

# 5 - A partir da lista de segmentos, será usado a biblioteca faster whisper, subdividindo o áudio a partir
# dos segmentos identificados e transcrevendo eles individualmente.

