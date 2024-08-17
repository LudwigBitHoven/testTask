## Описание решения
#### Часть с SQL / Python
Составим и выполним запрос для получения необходимых данных для дальнейшей агрегации:
```Python
query = ' \
    SELECT tv."date", p.partner, tv."values", tv."project"  FROM test_values tv \
    INNER JOIN partners p ON tv.partner_code = p.partner_code;'

df = pd.read_sql_query(query, connection)
```
#### Часть с Python
Конвертируем соответствующие строковые типы в int и datetime. Так как нас интересует помесячная доля накопленных в компании значений values, то убираем из рассмотрения дни:
```Python
df["date"] = pd.to_datetime(df["date"])
df["date"] = df["date"].apply(lambda dt: dt.strftime('%Y-%m'))
df["values"] = pd.to_numeric(df["values"])
```
Составим сводную таблицу, считающую сумму values с группировкой по проекту, месяцу и партнеру:
```Python
df_pivot = pd.pivot_table(
    df, 
    index=["project", "date", "partner"], 
    values="values", 
    aggfunc="sum")
```
Так как нас интересует доля значений values каждого месяца и каждой компании от всей суммы values за проект, то добавим столбец "% of values":
```Python
df_pivot["% of values"] = (df_pivot["values"] / df_pivot.groupby(level=0)["values"].transform(sum) * 100)
```
Код выше берет значения values из каждой группы и делит на сумму values по каждому проекту, умножая полученное число на 100, чтобы получить процент.
#### Дизайн таблицы
Таблица имеет столбцы "values" и "% of values", думаю с вспомогательным столбцом "values" таблица получается понятнее и красивее