#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pgdb
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import sys
mondbconn = pgdb.connect(user='postgres', password='', database='sympa')
cursor = mondbconn.cursor()

# Create new 7 days list
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
# print(weekly_list)

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
#print(subscribed_list)
cursor.close()
mondbconn.close()

# Send emails to users
for key, value in subscribed_list.iteritems():
    weekly_msg = '<html><head></head><body><b>New subscribtion lists for this week:</b><br>'
    sub_list = '<b>Your subscribtions:</b><br>'
    for name in value:
        sub_list += name + ' <a href="http://rdkmailer.ccp.xcal.tv/sympa/signoff/{0}">Unsubscribe</a><br>'.format(name)
    for name in weekly_list:
        if name in sub_list:
            weekly_msg += name + ' <b>new</b><br>'
        else:
            weekly_msg += name + ' <a href="http://rdkmailer.ccp.xcal.tv/sympa/subscribe/{0}">Subscribe</a><br>'.format(
                name)

    msg = MIMEText(weekly_msg + sub_list + '</body></html>', 'html')
    msg['Subject'] = 'RDK Mailing weekly subscription digest'
    msg['To'] = key
    print(msg.as_string())
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(msg.as_string())
