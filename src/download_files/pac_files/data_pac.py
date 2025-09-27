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


