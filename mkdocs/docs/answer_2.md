## Описание решения
В папке partners лежит несколько xlsx файлов, поэтому зальем их все, объединив их в один датафрейм.  
Для объединения xlsx реализована функция create_merged_df, получающая на вход список путей по которому расположены xslx-ки. Функция считывает файлы, добавляет созданыне на основе файлов датафреймы в список и конкатанирует список в конце выполнения цикла:
```Python
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
```
При нахождении дубликатов функция check_if_duplicates возвращает bool, который определяет дальнейшее выполнение скрипта:
```Python
def check_if_duplicates(df):
	"""
		checks whether dfs contain any dupliacte rows
	"""
	pivot = pd.pivot_table(df, values="partner_code", index="partner", aggfunc="count")
	if pivot[pivot["partner_code"] > 1].shape[0] == 0:
		return False
	return True
```
Для загрузки данных в бд используется функция to_sql из pandas:
```Python
df.to_sql("partners", con=connection, if_exists='append')
```
Кажется, что таблица revenue должна иметь внешний ключ к таблице partners, дальнейший скрипт неловко, но пытается добавить его. Это делается через создание вспомогательной таблицы с внешним ключом, импортом данных во вспомогательную таблицу и заменой старой таблицы свежесозданной.  
Это не эффективно, так как внесение всех данных заново тратит много времени, но желание добавить ключ берет верх:
```Python
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
```
