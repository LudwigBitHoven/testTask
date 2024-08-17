## Описание решения
#### Часть с SQL / Python
Таблица prices содержит nan значения, заданные через тип string. Превратим их в настоящие NULL:
```Python
cur.execute("""UPDATE prices SET price_start = NULL WHERE price_start = "nan";""")
cur.execute("""UPDATE prices SET price_start2 = NULL WHERE price_start2 = "nan";""")
cur.execute("""UPDATE prices SET price_test = NULL WHERE price_test = "nan";""")
```
Такой подход меняет данные в бд, но можно сделать аналогичную операцию, взяв дубликат таблицы; \
\
Составим и выполним запрос для получения необходимых данных для дальнейшей агрегации:
```Python
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
```
Выбор COALESCE оправдан большей читаемостью по сравнению с IFNULL \
#### Часть с Python
Конвертируем соответствующие строковые типы в int и datetime:
```Python
df["price_deal"] = pd.to_numeric(df["price_deal"])
df["product_price"] = pd.to_numeric(df["product_price"])
df["count"] = pd.to_numeric(df["count"])
```
Разделим год-месяц-день на год-месяц и день, поместим их в отдельные столбцы:
```Python
df["day"] = df["date_sale"].apply(lambda dt: dt.strftime('%d'))
df["date_sale"] = df["date_sale"].apply(lambda dt: dt.strftime('%Y-%m'))
```
По условию необходимо получить среднюю сдельную цену и цену товара по складу, партнеру и наименованию товара за первый квартал 2021 и 2022. Как я понял средняя цена должна находится за весь квартал по вышеописанным группам. Составим соответствующую сводную таблицу:
```Python
df_1 = pd.pivot_table(
    df, 
    index=["partner", "warehouse", "name_nom"],
    values=["product_price", "price_deal"],
    aggfunc="mean")
```
Как я понял по условию нам также необходимо найти количество реализованного товара по дням и сумму по реализованному товару за месяц. Составим сводную таблицу:
```Python
df_2 = pd.pivot_table(
    df, 
    index=["partner", "warehouse", "name_nom", "date_sale"],
    columns="day",
    values=["count"],
    aggfunc="sum",
    margins=True,
    fill_value=0)
```
Соединим две сводные таблицы через merge. Для этого удалим date_sale как индекс и установим его как столбец:
```Python
df_2.reset_index(level=['date_sale'], inplace=True)
df = pd.merge(df_1, df_2.droplevel(0, axis=1), left_index=True, right_index=True)
```
#### Дизайн таблицы
Итоговая таблица получилась довольно широкой из-за столбцов под каждый из дней месяца. Это сделано потому, что pivot_table в новых версиях не позволяет без 'ломания' pandas и вреда для рантайма делать строковые подитоги для каждой группы. В качестве альтернативы можно перенести строки месяцев в столбцы, а столбцы дней в строки, но текущий дизайн мне нравится больше