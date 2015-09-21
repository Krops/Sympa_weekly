#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pgdb
import sys,os

mondbconn = pgdb.connect(user='postgres', password='', database='sympa')
cursor = mondbconn.cursor()

#Test speed function
@profile
def sql_part():
    weekly_list = []
    sql_get_week_names = "select name_list from list_table where creation_time_list > current_timestamp - interval '7 days'"
    try:
        cursor.execute(sql_get_week_names)
    except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
        sys.exit(0)
    while (1):
        row = cursor.fetchone()
        if row is None:
            break
        else:
            try:
                weekly_list.append(row[0])
            except IndexError:
                sys.exit(0)
    #print(weekly_list)

    # Create list of subscribed users
    user_list = []
    sql_get_user_sub = "select distinct(user_subscriber) from subscriber_table"
    try:
        cursor.execute(sql_get_user_sub)
    except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
            sys.exit(0)
    while (1):
        row = cursor.fetchone()
        if row is None:
            break
        else:
            try:
                user_list.append(row[0])
            except IndexError:
                sys.exit(0)

    # Create user dict with their own subscribtion
    subscribed_list = {}
    for user in user_list:
        user_sub = []
        sql_get_list_sub = "select list_subscriber from subscriber_table where user_subscriber=%s"
        try:
            cursor.execute(sql_get_list_sub,(user,))
        except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
            print('Error to read {0} subscribtion'.format(user))
            sys.exit(0)
        while (1):
            row = cursor.fetchone()
            if row is None:
                break
            else:
                try:
                    user_sub.append(row[0])
                except IndexError:
                    sys.exit(0)
        subscribed_list[user] = user_sub
    print(subscribed_list)
    cursor.close()
    mondbconn.close()

#Execute sql_part function
if __name__ == "__main__":
    try:
        sql_part()
    except KeyboardInterrupt:
        print('\nQuit!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
