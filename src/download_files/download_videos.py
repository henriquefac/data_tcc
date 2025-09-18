from configPy import Config, DirManager
from pathlib import Path
from pytubefix.query import StreamQuery 
from pytubefix import YouTube

# valores de itag

ITAGS = ["251", "140", "139"]

# dicionario para mapear os tipos de arquivos para sua extenção correta

EXT_MAP = {
    "audio/webm": "webm",
    "audio/mp4": "m4a"
}

def select_stream(streamQuerry:StreamQuery):
    for itag in ITAGS:
        s = streamQuerry.get_by_itag(itag=itag)
        if s:
            return s

    return streamQuerry.order_by("abr").desc().first()


def download_single_audio(name_session: str, out_put_dir:DirManager, link_video: str, download_if_exists:bool = False):
    try:
        link_video = link_video.strip()
        yt = YouTube(link_video)
        stream = select_stream(yt.streams.filter(only_audio=True))
        if not stream:
            raise RuntimeError("Nenhum stream disponível")
        
        # identificar sufixo
        ext = EXT_MAP.get(stream.mime_type, ".m4a")

        filename = f"{name_session}.{ext}"
        output_dir_path = out_put_dir.dir_path
        
        if (output_dir_path / filename).exists() and download_if_exists:
            return f"Áudio já existe"

        output = stream.download(output_path=str(output_dir_path), filename=filename)
        return f"Áudio baixado do vídeo {link_video} em {output}"
    except Exception as e:
        return f"Erro ao baixar áudio do video {link_video}: {e}"



