#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pgdb

table_list = {}
current_table = ''
result_string = ''
mondbconn = pgdb.connect(user='postgres', password='', database='sympa')
cursor = mondbconn.cursor()
sql = "select name_list from list_table;"
list_names = []
try:
    cursor.execute(sql)
except:
    print "SQL query failed"
while (1):
    # считываем строку из ответа на SQL запрос
    row = cursor.fetchone()
    if row == None:
        break
    try:
        list_names.append(str(row[0]))

    except:
        print('Error to add list name')
print('Print all lists')
print(list_names)
print('\n')
for name in list_names:
    sql2 = "select list_admin,date_admin from admin_table where list_admin='" + name + "' order by date_admin limit 1"
    try:
        cursor.execute(sql2)
    except:
        print('Wrong SQL')
        break
    row = cursor.fetchone()
    try:
        table_list[row[0]] = row[1]
    except:
        print('error read list')

print('Print All lists and creation time')
print(table_list)
print('\n')
sql3 = "alter table list_table add column creation_time_list timestamp not null default current_timestamp"
try:
    cursor.execute(sql3)
    mondbconn.commit()
except:
    print("Sql Error to add new column")
for key, value in table_list.iteritems():
    sql4 = "update list_table SET creation_time_list='" + value + "' where name_list='" + key + "'"
    cursor.execute(sql4)
mondbconn.commit()
cursor.close()
mondbconn.close()
