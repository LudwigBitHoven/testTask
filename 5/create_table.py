import sqlite3

connection = sqlite3.connect('../test.db') # path to test.db
cur = connection.cursor()

query = ' \
CREATE TABLE "call_data" ( \
	"index" INTEGER, \
	"link" TEXT, \
	"importance" TEXT, \
	"incoming" TEXT, \
	"description" TEXT, \
	"topic" TEXT, \
	"comment" TEXT, \
	"number" TEXT, \
	"product_amount" TEXT);'

cur.execute(query)
connection.commit()
