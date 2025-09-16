from configPy import Config, DirManager
from src.url_links import get_df_query

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
