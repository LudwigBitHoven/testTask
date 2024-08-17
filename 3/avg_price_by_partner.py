import sqlite3
import pandas as pd

connection = sqlite3.connect('../test.db') # path to test.db
cur = connection.cursor()



""" 
	Convert absent prices to NULL in db, will be useful later in forming a query with COALESCE,
	TODO: would have been better to not modify the db and use the copy of the table
"""

cur.execute("""UPDATE prices SET price_start = NULL WHERE price_start = "nan";""")
cur.execute("""UPDATE prices SET price_start2 = NULL WHERE price_start2 = "nan";""")
cur.execute("""UPDATE prices SET price_test = NULL WHERE price_test = "nan";""")

""" 
	get raw data for pivoting, using COALESCE as it is more readable than IFNULL
	using ideas from the task 1 to improve query performance
"""
query = ' \
	SELECT \
		partner.partner, \
		r.warehouse, \
		g.name_nom,\
		COALESCE(prices.price_start, prices.price_start2, prices.price_test) as "product_price", \
		r.price_deal, \
		r.date_sale, \
		r.count \
	FROM \
		revenue r \
	INNER JOIN \
		guid g ON r.id_guid = g.id_guid \
	INNER JOIN \
		prices ON g.id_guid = prices.id_guid \
	INNER JOIN \
		partners partner ON r.partner_code = partner.partner_code \
	WHERE  \
		(r.date_sale BETWEEN "2020-01-01 00:00:00" AND "2020-04-01 00:00:00") OR \
		(r.date_sale BETWEEN "2021-01-01 00:00:00" AND "2021-04-01 00:00:00");'

# obtaining dataframe by query
df = pd.read_sql_query(query, connection)

# get data by first three months of 2021 and 2020
df["date_sale"] = pd.to_datetime(df["date_sale"])
df = df[
	(df["date_sale"].dt.month < 4) & 
	(df["date_sale"].dt.year.isin([2021, 2020]))
]

# convert aggregate columns to numeric (they were text in db)
df["price_deal"] = pd.to_numeric(df["price_deal"])
df["product_price"] = pd.to_numeric(df["product_price"])
df["count"] = pd.to_numeric(df["count"])

df["day"] = df["date_sale"].apply(lambda dt: dt.strftime('%d'))
df["date_sale"] = df["date_sale"].apply(lambda dt: dt.strftime('%Y-%m'))


# create pivot for average price without date
df_1 = pd.pivot_table(
	df, 
	index=["partner", "warehouse", "name_nom"],
	values=["product_price", "price_deal"],
	aggfunc="mean")

# create pivot for count by day and with sum to the right
df_2 = pd.pivot_table(
	df, 
	index=["partner", "warehouse", "name_nom", "day"],
	columns="day",
	values=["count"],
	aggfunc="sum",
	margins=True,
	fill_value=0)

# merge two pivots
df_2.reset_index(level=['date_sale'], inplace=True)
df = pd.merge(df_1, df_2.droplevel(0, axis=1), left_index=True, right_index=True)

# show output & save locally
df.to_csv("pivot_table.csv")