#### Описание решения
Подключимся к бд:
```Python
import sqlite3

connection = sqlite3.connect("test.db")

with connection:
	res = connection.execute("SELECT * FROM prices")
	print(res.fetchall())

```
