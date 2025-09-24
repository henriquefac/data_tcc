from src.url_links import query
from .data_pac import (Pac, PacATAS, 
    PacAUDIOS, PacFULL, TypeKeys)

def get_files_by_year(n:int, key:TypeKeys | list[TypeKeys]) -> Pac:
    pac_class = Pac
    if isinstance(key, list):
        keys = sorted([k.value for k in key])
        keys.append("session_name")
        pac_class = PacFULL
    else:
        keys = [key.value, "session_name"]
        pac_class = PacATAS if key == TypeKeys.URL else PacAUDIOS
    df = query.query_by_group("year", n, keys)

    new_dict = {}

    for year in df:
        tuplas = list(df[year][keys].itertuples(index=False, name=None))
        new_dict[year] = tuplas
    
    return pac_class.get_pac(new_dict, ["year", str(n)] + (keys))

def get_files_by_year_url(n: int) -> PacATAS:
    return get_files_by_year(n, TypeKeys.URL)

def get_files_by_year_link(n: int) -> PacAUDIOS:
    return get_files_by_year(n, TypeKeys.LINK)

def get_files_by_year_url_link(n: int) -> PacFULL:
    return get_files_by_year(n, [TypeKeys.URL, TypeKeys.LINK])
