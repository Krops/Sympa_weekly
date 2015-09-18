#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pgdb
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

mondbconn = pgdb.connect(user='postgres', password='46KNVgw274', database='sympa')
cursor = mondbconn.cursor()
# Create new 7 days list
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
# Send emails to users

weekly_msg = '<html><head></head><body><b>New subscribtion lists for this week:</b><br>'
for key, value in subscribed_list.iteritems():
    sub_list = '<b>Your subscribtions:</b><br>'  # +'\n'.join(value) + '\n<a href="http://rdkmailer.ccp.xcal.tv/sympa/subscribe/">'+value+'</a>'
    for name in value:
        sub_list += name + ' <a href="http://rdkmailer.ccp.xcal.tv/sympa/signoff/' + name + '">Unsubscribe</a><br>'
    for name in weekly_list:
        if name in sub_list:
            weekly_msg += name + '<br>'
        else:
            weekly_msg += name + ' <a href="http://rdkmailer.ccp.xcal.tv/sympa/subscribe/' + name + '">Subscribe</a><br>'

    msg = MIMEText(weekly_msg + sub_list + '</body></html>', 'html')
    msg['Subject'] = 'RDK Mailing weekly subscription digest'
    msg['To'] = key
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(msg.as_string())
