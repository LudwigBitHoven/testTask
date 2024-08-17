import pandas as pd
import sqlite3
from typing import List
from os import listdir
from os.path import join
from sqlalchemy import create_engine # used in pandas to_sql function


SQLITE_PATH = "sqlite://../test.db"
LOCAL_DB_PATH = "../test.db"
DATA_PATH = "../partners"


def create_merged_df(paths: List[str]):
	"""
		concatenates all dfs in the directory in a single one to rule them all
	"""
	dfs = []
	for path in paths:
		temp = pd.read_excel(path, sheet_name=None)["Sheet1"]
		dfs.append(temp)

	df = pd.concat(dfs)
	df.columns = ["partner", "partner_code"]
	return df

def check_if_duplicates(df):
	"""
		checks whether dfs contain any dupliacte rows
	"""
	pivot = pd.pivot_table(df, values="partner_code", index="partner", aggfunc="count")
	if pivot[pivot["partner_code"] > 1].shape[0] == 0:
		return False
	return True

def load_data(dir_path):
	"""
		entry point for loading data from directory to sqlite db
	"""
	# creates paths to all files in the given directory dir_path
	paths = [join(dir_path, f) for f in listdir(dir_path)]
	df = create_merged_df(paths)
	
	if check_if_duplicates(df):
		print("Abort, dfs have duplicates")
		return False
	
	# creates table for partners
	connection = create_engine(SQLITE_PATH) # needs abs path to test.db
	df.to_sql("partners", con=connection, if_exists='append')
	return True

def create_foreign_key():
	"""
		whacky sql query for creating FOREIGN KEY constraint in revenue;
		renames old table, creates new one with the FOREIGN KEY constraint, 
		loads data from the old to the new table and finally drops the old table
	"""
	connection = sqlite3.connect("../test.db") # path to test.db
	cur = connection.cursor()
	cur.execute("""ALTER TABLE "revenue" RENAME TO "revenue_old";""")
	cur.execute(
	"""
		CREATE TABLE "revenue" (
			"index" INTEGER,
			"id_guid" TEXT,
			"date_sale" TEXT,
			"warehouse" TEXT,
			"registr" TEXT,
			"partner_code" TEXT,
			"count" TEXT,
			"price_deal" TEXT,
			FOREIGN KEY(partner_code) REFERENCES partners(partner_code));
	""");
	cur.execute("""INSERT INTO "revenue" SELECT * FROM "revenue_old";""")
	cur.execute("""DROP TABLE "revenue_old";""")
	connection.commit()


if __name__ == "__main__":
	load_data(DATA_PATH)
	create_foreign_key()
