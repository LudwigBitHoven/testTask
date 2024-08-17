## Описание решения
#### Скрипты и их назначение
**create_table.py** - создает таблицу, в которую данные будут загружатся  
**modify_xlsx.py** - редактирует файлы xlsx, чтобы их можно было загрузить в pandas без ошибок  
**upload_data.py** - загружает данные из исправленных xlsx-ок в бд  
#### Код create_table.py
Все довольно прозаично - код создает таблицу в бд:
```Python
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

```
#### Код modify_xlsx.py
Тут немного сложнее. Pandas не может прочитать файл, так как метафайл "xl/**s**haredStrings.xml" внутри xlsx имеет название со сбитым регистром и назван "xl/**S**haredStrings.xml" (возможно это была ошибка при сохранении).  
Открывать файл напрямую не хочется, так как xlsx представляет собой архив, и это повлечет за собой разархивирование, архивирование обратно и трату времени.  
Чтобы сделать всё красиво:
* откроем архив для чтения, 
* скопируем отредактированные данные и все остальное в новый архив, 
* старый архив удалим позже вручную или через os.remove, как убедимся что все залито правильно. \
Для начала соберем путь до всех xlsx-ок в директории:
```Python
from os import listdir
from os.path import join, isfile
import zipfile


PATH = "../заливка"
paths = [join(PATH, f) for f in listdir(PATH) if isfile(join(PATH, f))]
```
Используем контекстный менеджер для работы с файлами архивов:
```Python
try:
    for path in paths:
        """
            renames 'xl/SharedStrings.xml' into 'xl/sharedStrings.xml' inside xlsx file,
            works without extracting files, new files have names like "file_name.modified.xlsx"
        """
        # opens old archive
        with zipfile.ZipFile(path, mode="r") as archive:
            # opens new archive
            with zipfile.ZipFile(path + "_temp.xlsx", 'w') as temp_zip:
                # reads data from old archive
                for item in archive.infolist():
                    # saves data in new archive modifying the xl/SharedStrings.xml
                    if item.filename == 'xl/SharedStrings.xml':
                        temp_zip.writestr('xl/sharedStrings.xml', archive.read(item.filename))
                    else:
                        temp_zip.writestr(item.filename, archive.read(item.filename))
    print("Script finished successfully")
except Exception as E: # not really nice
    print(f"Error occured:\n{E}")
```
#### Код upload_data.py
Соберем пути до отредактированных файлов в директории и создадим объект connection:
```Python
import pandas as pd
from os import listdir
from os.path import join, isfile
from sqlalchemy import create_engine


SQLITE_PATH = "sqlite:///C:/Users/nickc/Desktop/Задания/test.db"
PATH = "../заливка"
paths = [join(PATH, f) for f in listdir(PATH) if (isfile(join(PATH, f)) and ("_temp.xlsx" in f))]

connection = create_engine(SQLITE_PATH)
```
Чтобы не хардкодить название столбцов в бд возьмем их напрямую:
```Python
# obtain table with names
db_column_names = pd.read_sql_query("PRAGMA table_info(call_data);", connection)
# get names from the table excluding index [1:]
db_column_names = db_column_names["name"].tolist()[1:]
# cast to tuple
db_column_names = tuple(db_column_names)
```
Загрузим данные в бд:
```Python
try:
    for path in paths:
        # ignore 7 rows with metadata
        df = pd.read_excel(path, header=7, sheet_name=None)["TDSheet"]
        # drop unnamed
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        # rename columns
        df.columns = db_column_names
        # load to db
        df.to_sql("call_data", con=connection, if_exists='append')
    print("Finished successfully")
except Exception as E: # not really nice
    print(f"Error occured:\n{E}")
```
Код выше пропускает 7 строк с метаданными таблицы (надо ли их добавлять?), удаляет безымянные столбцы, именует столбцы согласно ранее полученным названиям и загружает в бд