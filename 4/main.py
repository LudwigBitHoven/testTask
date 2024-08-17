import sqlite3
import pandas as pd

connection = sqlite3.connect('../test.db') # path to test.db
cur = connection.cursor()

query = ' \
	SELECT tv."date", p.partner, tv."values", tv."project"  FROM test_values tv \
	INNER JOIN partners p ON tv.partner_code = p.partner_code;'

df = pd.read_sql_query(query, connection)

# cast to needed types
df["date"] = pd.to_datetime(df["date"])
df["date"] = df["date"].apply(lambda dt: dt.strftime('%Y-%m'))
df["values"] = pd.to_numeric(df["values"])

# solution does not include months with absent values
df_pivot = pd.pivot_table(
	df, 
	index=["project", "date", "partner"], 
	values="values", 
	aggfunc="sum")

# calculates share of monthly grouped sums of values in a company
df_pivot["% of values"] = (df_pivot["values"] / df_pivot.groupby(level=0)["values"].transform(sum) * 100)

print(df_pivot)
df_pivot.to_csv("pivot_table.csv")
