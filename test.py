from src.url_links import query, get_df_query

df = query.query_sessions()

df = query.query_groupby(df, query.GroupKeys.ANO, "list")
print(df["url"])
