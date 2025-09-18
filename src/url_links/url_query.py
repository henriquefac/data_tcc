from configPy import Config, DirManager
from src.url_links import get_df_query
from enum import Enum
import pandas as pd
import numpy as np

class GroupKeys(Enum):
    ANO = "year"
    SCORE = "score"

def query_sessions(year: int | None = None) -> pd.DataFrame:
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

def query_by_group(key_str: str, n_lines: int, keys_list_atr: list[str]):
    df = query_sessions()
    df_grouby = df.groupby(key_str, sort=False)
    
    dfs_samples = {}

    for key, group in df_grouby:
        df_subset = group[keys_list_atr]
        n = len(df_subset)

        range_steeps = np.linspace(0, n-1, min(n_lines, n), dtype=int)
        sample = df_subset.iloc[range_steeps]
        dfs_samples[key] = sample
    return dfs_samples
        

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



