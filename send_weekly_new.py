#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pgdb
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import sys
import ldap
import os
import re
mondbconn = pgdb.connect(user='sympa_user', password='', database='sympa', host='localhost')
cursor = mondbconn.cursor()


# Create new 7 days list
weekly_list = []
sql_get_week_names = "select name_list from list_table where status_list='open' and creation_time_list > current_timestamp - interval '7 days'"
try:
    cursor.execute(sql_get_week_names)
except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
        sys.exit(1)
while (1):
    row = cursor.fetchone()
    if row is None:
        break
    else:
        try:
            weekly_list.append(row[0])
        except IndexError:
            sys.exit(1)
# for testing
#weekly_list = ['arris_xg1v3-daily-changes', 'rdktools-dev', 'samsung_xg2v1-daily-changes']

# Create list of subscribed users
user_list = []
sql_get_user_sub = "select distinct(user_subscriber) from subscriber_table"
try:
    cursor.execute(sql_get_user_sub)
except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
        sys.exit(1)
while (1):
    row = cursor.fetchone()
    if row is None:
        break
    else:
        try:
            user_list.append(row[0])
        except IndexError:
            sys.exit(1)

# Create user dict with their own subscribtion
subscribed_list = {}
for user in user_list:
    user_sub = []
    sql_get_list_sub = "select list_subscriber from subscriber_table where user_subscriber=%s"
    try:
        cursor.execute(sql_get_list_sub,(user,))
    except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
        print('Error to read {0} subscribtion'.format(user))
        sys.exit(1)
    while (1):
        row = cursor.fetchone()
        if row is None:
            break
        else:
            try:
                user_sub.append(row[0])
            except IndexError:
                sys.exit(1)
    subscribed_list[user] = user_sub
cursor.close()
mondbconn.close()

allowedGroups = {}
for dir in weekly_list:
    try:
        try:
            file=open('/mnt/sympa/list_data/{0}/config'.format(dir),'r')
        except:
            file=open('/home/sympa/list_data/{0}/config'.format(dir),'r')
            print("{0} in home".format(dir))
    except IOError as e:
        #print "I/O error({0}): {1}".format(e.errno, e.strerror)
        continue
    text = file.read()
    res_groups = []
    tes_str = re.findall(r'custom_vars\nvalue (.*)\n', text)
    for lst in tes_str:
        groups = [group.strip() for group in lst.split(',')]
        res_groups += groups
    if len(res_groups)>0:
        allowedGroups[dir]=res_groups
    else:
        continue
    file.close()
print(weekly_list)
print(allowedGroups)

# ldap initialize
ldap_client = ldap.initialize('')
ldap_base = 'ou=CCP,dc=ra,dc=ccp,dc=cable,dc=comcast,dc=com'

# Send emails to users
for key, value in subscribed_list.iteritems():
    weekly_msg = '<h3>New subscribtion lists for this week:</h3>'
    test_wm = weekly_msg
    sub_list = '<html><head></head><body><h3>Your subscribtions:</h3>'
    email_info = ldap_client.search_s(ldap_base, ldap.SCOPE_SUBTREE, '(mail={0})'.format(key))
    try:
        user_uid = email_info[0][1]['uid'][0]
    except:
        user_uid = None
    for name in value:
        sub_list += '<div><label>{0}: </label><a href="https://rdklistmgr.ccp.xcal.tv/sympa/signoff/{0}">unsub</a></div>'.format(name)
    for name in weekly_list:
        if name in allowedGroups:
            for group in allowedGroups[name]:
                ldap_info_group = ldap_client.search_s(ldap_base, ldap.SCOPE_SUBTREE, '(cn={0})'.format(group))
                try:
                    if user_uid in ldap_info_group[0][1].get('memberUid', []):
                        if name in sub_list:
                            weekly_msg += '<div><label>{0}: </label><b>new</b></div>'.format(name)
                            break
                        else:
                            weekly_msg += '<div><label>{0}: </label><a href="https://rdklistmgr.ccp.xcal.tv/sympa/subscribe/{0}">sub</a></div>'.format(name)
                            break
                except:
                    continue
        else:
            continue
    if weekly_msg==test_wm:
        weekly_msg=''
    msg = MIMEText('{0}<br>{1}</body></html>'.format(sub_list,weekly_msg), 'html')
    msg['Subject'] = 'RDK Mailing weekly subscription digest'
    msg['To'] = key
    print(key)
    #if 'ababich' in key:
        #print(msg.as_string())
        #p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        #p.communicate(msg.as_string())
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(msg.as_string())
