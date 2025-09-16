from configPy import Config, DirManager
from pathlib import Path
import pandas as pd
import re

files_dir = Config.get_dir_files()
sessoes_dir = files_dir["sessoes_url"]


# get all files
def get_all_files():
    return list(sessoes_dir.list_files().values())


def semp_for_date(url_str: str) -> str:
    """Extrai a parte central do nome da sessão, sem a extensão."""
    return url_str.rsplit(".", 1)[0].split("|")[2]


def aux_get_subname(url_str: str) -> str:
    return semp_for_date(url_str).replace(".", "-")


def parse_session_date(url_str: str) -> pd.Timestamp:
    """
    Extrai a data do campo do tipo:
    2021|04|sessao-de-6-4.2021|Ata25.pdf
    """
    try:
        parts = url_str.split("|")
        session_part = parts[2]  # ex: "sessao-de-6-4.2021"

        # Regex: dia-mes.ano (ano pode ter sufixo -n)
        m = re.search(r"(\d{1,2})-(\d{1,2})\.(\d{4})(?:-\d+)?", session_part)
        if m:
            d, mm, y = map(int, m.groups()[:3])
            return pd.Timestamp(year=y, month=mm, day=d)
        return pd.NaT
    except Exception:
        return pd.NaT


def load_csv(path_csv: Path) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(path_csv, header=None, names=["url", "links"])
        df["session_name"] = df["url"].apply(aux_get_subname)
        df["date"] = df["url"].apply(parse_session_date)

        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"] = df["date"].dt.day
        df["score"] = df["date"].dt.strftime("%Y%m%d").astype(int)

        return df
    except Exception as e:
        print(f"erro ao carregar csv '{path_csv}': {e}")
        return None


def filter_by_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Retorna apenas as sessões de um determinado ano."""
    return df[df["year"] == year].copy()


def combine_all_csv(output_dir_path: DirManager | None = None, filter_year: int | None = None):
    if output_dir_path is None:
        output_dir_path = sessoes_dir
    namefile = "query_url_links"
    if filter_year is not None:
        namefile += f"_{filter_year}"
    
    file_name_path = output_dir_path.create_file_path(namefile, "csv")
    all_dfs = []
    
    for f in get_all_files():
        df = load_csv(f)
        if df is not None and not df.empty:
            all_dfs.append(df)

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df = combined_df.sort_values("date")

        if filter_year is not None:
            combined_df = filter_by_year(combined_df, filter_year)

        combined_df.to_csv(file_name_path, index=False, encoding="utf-8")
        print(f"Arquivo combinado salvo em: {file_name_path}")
        return combined_df
    else:
        print("Nenhum dado encontrado nos arquivos.")
        return pd.DataFrame()


def get_df_query(year: int | None = None):
    try:
        namefile = "query_url_links"
        if year:
            namefile += f"_{year}"

        # garantir que estamos pegando o arquivo certo
        filequery = sessoes_dir.get_file_path(namefile, "csv")
        df = pd.read_csv(filequery)
        
        return filter_by_year(df, year) if year else df
    except Exception:
        return combine_all_csv(output_dir_path=None, filter_year=year)
