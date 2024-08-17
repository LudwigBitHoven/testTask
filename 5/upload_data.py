import pandas as pd
from os import listdir
from os.path import join, isfile
from sqlalchemy import create_engine


SQLITE_PATH = "sqlite://../test.db"
PATH = "../заливка"
paths = [join(PATH, f) for f in listdir(PATH) if (isfile(join(PATH, f)) and ("_temp.xlsx" in f))]


connection = create_engine(SQLITE_PATH)

""" 
	given data do not correspond to the db names of the columns,
	will substitute names in cyrillic by ones in the tuple
	TODO: get db column names from query to avoid hardcoding
"""

db_column_names = pd.read_sql_query("PRAGMA table_info(call_data);", connection)
db_column_names = tuple(db_column_names["name"].tolist()[1:])

try:
	for path in paths:
		df = pd.read_excel(path, header=7, sheet_name=None)["TDSheet"]
		df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
		df.columns = db_column_names
		df.to_sql("call_data", con=connection, if_exists='append')
	print("Finished successfully")
except Exception as E:
	print(f"Error occured:\n{E}")
