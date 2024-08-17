## 1. Задача
Дан запрос, который необходимо оптимизировать:
```sql
select distinct partner_code,vid_nom, warehouse, sum(count) over (partition by partner_code,vid_nom) from guid g, prices p, revenue r
where g.id_guid = p.id_guid and p.id_guid = r.id_guid;
```
Первая проблема - это использование DISTINCT и OVER. Эти операции можно заменить простым GROUP BY в конце запроса
```sql
select partner_code,vid_nom, warehouse, sum(count) from guid g, prices p, revenue r
where g.id_guid = p.id_guid and p.id_guid = r.id_guid
GROUP BY partner_code, vid_nom, warehouse;
```
Вторая проблема - это имплицитный join, который ухудшает читаемость кода, заменим его на INNER JOIN
```sql
SELECT r.partner_code, g.vid_nom, r.warehouse, sum(r.count) FROM guid g
INNER JOIN revenue r ON p.id_guid = r.id_guid
INNER JOIN prices p ON g.id_guid = p.id_guid
GROUP BY r.partner_code, g.vid_nom, r.warehouse;
```
Третья проблема - это join большой таблицы revenue к таблице guid со всеми её столбцами, поменяем местами "guid g" и "revenue r" в функциях join и from.
Дадим столбцу с суммой по count более информативное название

```sql
SELECT r.partner_code, g.vid_nom, r.warehouse, sum(r.count) AS "count sum" FROM revenue r
INNER JOIN guid g ON p.id_guid = r.id_guid
INNER JOIN prices p ON g.id_guid = p.id_guid
GROUP BY r.partner_code, g.vid_nom, r.warehouse;
```
Итого время выполнения до оптимизации составляло 36.423 с, после 1.414 с.