from src.url_links import query 
from typing import Generator
from src.download_files.pac_files.data_pac import (
Pac, PacATAS, PacAUDIOS, PacFULL, TypeKeys)

DotValue = query.DotValue

def get_files_by_porcent(
        dot_value: DotValue,
        key: TypeKeys | list[TypeKeys]
) -> Generator:
    pac_class = Pac
    if isinstance(key, list):
        keys = sorted([k.value for k in key])
        keys.append("session_name")
        pac_class = PacFULL
    else:
        keys = [key.value, "session_name"]
        pac_class = PacATAS if key == TypeKeys.URL else PacAUDIOS

    df = query.query_sessions()

    for i, df_part in enumerate(query.query_inter_dot(df, "year",dot_value, keys)):
        new_dict = {}
        for year in df_part:
            tuplas = list(df_part[year][keys].itertuples(index=False, name=None))
            new_dict[year] = tuplas
        yield pac_class.get_pac(new_dict, ["year", f"{dot_value.name}[{i}]"] + keys)

def get_files_by_porcent_url(dot_value: DotValue)->Generator:
    return get_files_by_porcent(dot_value, TypeKeys.URL)

def get_files_by_porcent_link(dot_value: DotValue)->Generator:
    return get_files_by_porcent(dot_value, TypeKeys.LINK)

def get_files_by_porcent_url_link(dot_value: DotValue)->Generator:
    return get_files_by_porcent(dot_value, [TypeKeys.LINK, TypeKeys.URL])
