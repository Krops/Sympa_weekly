#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pgdb
import sys,os

mondbconn = pgdb.connect(user='postgres', password='', database='sympa')
cursor = mondbconn.cursor()


# Create new 7 days list


@profile
def sql_part():
    weekly_list = []
    sql5 = "select name_list from list_table where creation_time_list > current_timestamp - interval '7 days'"
    try:
        cursor.execute(sql5)
    except:
        print('Error to create sql request 7 days list')
    while (1):
        row = cursor.fetchone()
        if row == None:
            break
        try:
            weekly_list.append(row[0])
        except:
            print('Error read sql request')
    print(weekly_list)
    # Create list of subscribed users
    user_list = []
    sql6 = "select distinct(user_subscriber) from subscriber_table"
    try:
        cursor.execute(sql6)
    except:
        print('Error Sql get users')
    while (1):
        row = cursor.fetchone()
        if row == None:
            break
        try:
            user_list.append(row[0])
        except:
            print('Error read sql request')
    # Create user dict with their own subscribtion
    subscribed_list = {}
    for user in user_list:
        user_sub = []
        sql7 = "select list_subscriber from subscriber_table where user_subscriber='" + user + "'"
        try:
            cursor.execute(sql7)
        except:
            print('Error to read ' + user + ' subscribtion')
            continue
        while (1):
            row = cursor.fetchone()
            if row == None:
                break
            user_sub.append(row[0])
        subscribed_list[user] = user_sub
    print(subscribed_list)
    cursor.close()
    mondbconn.close()


if __name__ == "__main__":
    try:
        sql_part()
    except KeyboardInterrupt:
        print('\nQuit!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
