from src.url_links import query
from enum import Enum
from dataclasses import dataclass
import hashlib

class TypeKeys(Enum):
    URL = "url"
    LINK = "links"


def hash_strings_sha256(strings: list[str])->str:
    h = hashlib.sha256()
    for s in strings:
        encoded = f"{len(s)}:".encode('utf-8') + s.encode('utf-8')
        h.update(encoded)
    return h.hexdigest()

@dataclass
class Pac:
    structure:dict
    hash:str
    
    @classmethod
    def get_pac(cls, structure:dict, list_params:list[str]) -> "Pac":
        return cls(
            structure=structure,
            hash=hash_strings_sha256(list_params)
        )
    

class PacATAS(Pac):
    pass

class PacAUDIOS(Pac):
    pass

class PacFULL(Pac):
    pass


def get_files_by_year(n:int, key:TypeKeys | list[TypeKeys]):
    pac_class = Pac
    if isinstance(key, list):
        keys = sorted([k.value for k in key])
        keys.append("session_name")
        pac_class = PacFULL
    else:
        keys = [key.value, "session_name"]
    df = query.query_by_group("year", n, keys)

    new_dict = {}

    for year in df:
        tuplas = list(df[year][keys].itertuples(index=False, name=None))
        new_dict[year] = tuplas
    
    return pac_class.get_pac(new_dict, ["year", str(n)] + (keys))


