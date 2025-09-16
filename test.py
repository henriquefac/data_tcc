from src.url_links import query
import pandas as pd
from json import loads, dumps

df = query.query_sessions()

df = query.query_groupby_steeps(df, query.GroupKeys.ANO, "url", 4)
print(dumps(df.to_json(), indent=4))




