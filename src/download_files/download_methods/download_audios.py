from configPy import DirManager
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



def download_single_file_audio(link:str, file_name:str, output_dir: DirManager):
    try:
        link = link.strip()
        yt = YouTube(link)
        stream = select_stream(yt.streams.filter(only_audio=True))
        if not stream:
            return f"Nenhum stream disponível para {link}"
        ext = EXT_MAP.get(stream.mime_type, "m4a")
        
        filename_suffix = f"{file_name}.{ext}"
        output_dir_path = str(output_dir.dir_path)

        output = stream.download(output_path=output_dir_path, filename=filename_suffix)
        return f"Áudio baixado do {link} em {output_dir_path}"

    except Exception as e:
        return f"Erro ao baixar áudio de {link}: {e}"
          
