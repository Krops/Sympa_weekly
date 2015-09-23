#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pgdb
import sys

table_list = {}
current_table = ''
result_string = ''
mondbconn = pgdb.connect(user='postgres', password='', database='sympa', host='localhost')
cursor = mondbconn.cursor()

# Get all list names from list_table
get_list_names = "select name_list from list_table;"
list_names = []
try:
    cursor.execute(get_list_names)
except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
    sys.exit(1)
while (1):
    row = cursor.fetchone()
    if row is None:
        break
    else:
        try:
            list_names.append(str(row[0]))
        except IndexError:
            sys.exit(1)
print('Print all lists')
print(list_names)
print('\n')

# Get creators and creation data
for name in list_names:
    sql_get_creator_date_list = "select list_admin,date_admin from admin_table where list_admin=%s  order by date_admin limit 1"
    try:
        cursor.execute(sql_get_creator_date_list, (name,))
    except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
        sys.exit(1)
    row = cursor.fetchone()
    if row is None:
        break
    else:
        try:
            table_list[row[0]] = row[1]
        except IndexError:
            sys.exit(1)

print('Print All lists and creation time')
print(table_list)
print('\n')

# Add creation_time_list column to list_table
sql_add_new_col_list = "alter table list_table add column creation_time_list timestamp not null default current_timestamp"
try:
    cursor.execute(sql_add_new_col_list)
    mondbconn.commit()
except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
    sys.exit(1)
for key, value in table_list.iteritems():
    sql_update_list = "update list_table SET creation_time_list=%s where name_list=%s"
    try:
        cursor.execute(sql_update_list, (value, key))
    except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
        sys.exit(1)
mondbconn.commit()
cursor.close()
mondbconn.close()
