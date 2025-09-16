from configPy import Config, DirManager
from src.url_links import get_df_query
from enum import Enum
import pandas as pd
import numpy as np

class GroupKeys(Enum):
    ANO = "year"
    SCORE = "score"

def query_sessions(year: int | None = None):
    """
    Retorna DataFrame ordenado por score (menor → maior).
    Se `year` for passado, filtra apenas para esse ano.
    """
    df = get_df_query(year)
    if df is None or df.empty:
        print("Nenhum dado encontrado.")
        return df

    df_sorted = df.sort_values("score", ascending=True).reset_index(drop=True)
    return df_sorted


def query_by_steeps(df: pd.DataFrame, n_of_lines: int) -> pd.DataFrame:
    """
    Retorna um subconjunto do DataFrame com `n_of_lines` linhas
    escolhidas de forma equidistante ao longo do DataFrame.
    """
    total_lines = df.shape[0]

    if total_lines == 0 or n_of_lines <= 0:
        return pd.DataFrame(columns=df.columns)

    if n_of_lines >= total_lines:
        return df.copy().reset_index(drop=True)


    indices = np.linspace(0, total_lines - 1, n_of_lines, dtype=int)
    df_sample = df.iloc[indices].reset_index(drop=True)

    return df_sample


def query_groupby(
    df: pd.DataFrame, 
    key: GroupKeys | list[GroupKeys], 
    agg: dict | str = "count"
) -> pd.DataFrame:
    """
    Agrupa o DataFrame por uma ou mais chaves definidas no Enum GroupKeys,
    garantindo que os dados sejam ordenados pelo score antes do agrupamento.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    key : GroupKeys | list[GroupKeys]
        Coluna(s) de agrupamento (restrita(s) ao Enum).
    agg : dict | str
        Operações de agregação (ex.: {"score": "mean"} ou "list").
        - "count" → conta linhas
        - "list"  → junta os valores em listas, ordenadas por score
    
    Returns
    -------
    pd.DataFrame
    """
    # Ordenar antes pelo score (se existir no DF)
    if "score" in df.columns:
        df = df.sort_values("score", ascending=True).reset_index(drop=True)

    # Se passar lista de enums → transformar em lista de strings
    if isinstance(key, list):
        keys = [k.value for k in key]
    else:
        keys = [key.value]

    # Validar colunas
    for k in keys:
        if k not in df.columns:
            raise ValueError(f"Coluna '{k}' não encontrada no DataFrame.")

    # Definir agregação
    if agg == "list":
        result = df.groupby(keys, sort=False, dropna=False).agg(list)
    elif isinstance(agg, dict):
        result = df.groupby(keys, sort=False, dropna=False).agg(agg).reset_index()
    else:
        result = df.groupby(keys, sort=False, dropna=False).size().reset_index(name="count")

    return result


def query_groupby_dict_steeps(
    df: pd.DataFrame,
    key: str,
    value_col: str,
    n_of_lines: int
) -> dict:
    """
    Agrupa o DataFrame por `key` e retorna um dicionário
    {chave: [valores]} onde cada lista é reduzida para no
    máximo `n_of_lines` elementos de forma equidistante.
    """
    import numpy as np

    # Ordenar pelo score para garantir consistência
    if "score" in df.columns:
        df = df.sort_values("score", ascending=True)

    result = {}
    for group_key, group_df in df.groupby(key, sort=False):
        total_lines = group_df.shape[0]

        if total_lines <= n_of_lines:
            sampled = group_df
        else:
            indices = np.linspace(0, total_lines - 1, n_of_lines, dtype=int)
            sampled = group_df.iloc[indices]

        result[group_key] = sampled[value_col].tolist()

    return result

__all__ = ["query_by_steeps", "query_groupby", "query_sessions", "query_groupby_dict_steep"]
