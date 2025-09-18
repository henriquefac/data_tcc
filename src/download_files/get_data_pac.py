from src.url_links import query
from enum import Enum

class TypeKeys(Enum):
    URL = "url"
    LINK = "links"


def get_files_by_year(n:int, key:TypeKeys | list[TypeKeys]):
    if isinstance(key, list):
        keys = [k.value for k in key]
        keys.append("session_name")
    else:
        keys = [key.value, "session_name"]
    df = query.query_by_group("year", n, keys)

    new_dict = {}

    for year in df:
        tuplas = list(df[year][keys].itertuples(index=False, name=None))
        new_dict[year] = tuplas
    
    return new_dict

def get_files_by_year_url(n: int):
    return get_files_by_year(n, TypeKeys.URL)

def get_files_by_year_link(n: int):
    return get_files_by_year(n, TypeKeys.LINK)

def get_files_by_year_url_link(n: int):
    return get_files_by_year(n, [TypeKeys.URL, TypeKeys.LINK])
