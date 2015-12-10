#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pgdb
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import sys
import ldap
import os
import re
mondbconn = pgdb.connect(user='sympa_user', password='WyLLSte9un', database='sympa', host='localhost')
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
# for testing!!!!!!!!!!!!!!!!!!!
weekly_list = ['rdktools-dev']
# print(weekly_list)

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
#print(subscribed_list)
cursor.close()
mondbconn.close()
#print(subscribed_list)

allowedGroups = {} #{'test-list':['rdk_employees', 'rdk_contractors', 'rdk_motorola']}
print(weekly_list)
for dir in weekly_list:
    try:
        try:
            file=open('/mnt/sympa/list_data/{0}/config'.format(dir),'r')
        except:
            file=open('/home/sympa/list_data/{0}/config'.format(dir),'r')
            print("{0} in home".format(dir))
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
    text = file.read()
    try:
        tes_str = re.search(r'custom_vars\nvalue ([a-z_-]+)(, [a-z_-]+)*',text).group(0)
        tes_list = tes_str.replace('custom_vars\nvalue ','').split(', ')
        allowedGroups[dir]=tes_list
    except:
        continue
    file.close()
print(allowedGroups)

# ldap initialize
ldap_client = ldap.initialize('ldap://ldap.ae.ccp.cable.comcast.com:1389')
ldap_base = 'ou=CCP,dc=ra,dc=ccp,dc=cable,dc=comcast,dc=com'
#tesl = ldap_client.search_s(ldap_base, ldap.SCOPE_SUBTREE, '(cn={0})'.format('rdk_employee'))
#print(tesl)
# Send emails to users
for key, value in subscribed_list.iteritems():
    weekly_msg = '<h3>New subscribtion lists for this week:</h3>'
    sub_list = '<html><head></head><body><h3>Your subscribtions:</h3>'
    #print(key)
    email_info = ldap_client.search_s(ldap_base, ldap.SCOPE_SUBTREE, '(mail={0})'.format(key))
    try:
        user_uid = email_info[0][1]['uid'][0]
    except:
        #print(key)
        #print('non rdk user')
        user_uid = None
    for name in value:
        sub_list += '<div><label>{0}: </label><a href="https://rdklistmgr.ccp.xcal.tv/sympa/signoff/{0}">unsub</a></div>'.format(name)
    for name in weekly_list:
        if name in allowedGroups:
            #print(allowedGroups[name])
            for group in allowedGroups[name]:
                ldap_info_group = ldap_client.search_s(ldap_base, ldap.SCOPE_SUBTREE, '(cn={0})'.format(group))
                try:
                    if user_uid in ldap_info_group[0][1].get('memberUid', []):
                        print(user_uid)
                        if name in sub_list:
                            print("fine")
                            weekly_msg += '<div><label>{0}: </label><b>new</b></div>'.format(name)
                            break
                        else:
                            print("fine too")
                            weekly_msg += '<div><label>{0}: </label><a href="https://rdklistmgr.ccp.xcal.tv/sympa/subscribe/{0}">sub</a></div>'.format(name)
                            break
                except:
                    continue
        else:
            if name in sub_list:
                weekly_msg += '<div><label>{0}: </label><b>new</b></div>'.format(name)
            else:
                weekly_msg += '<div><label>{0}: </label><a href="https://rdklistmgr.ccp.xcal.tv/sympa/subscribe/{0}">sub</a></div>'.format(name)
    msg = MIMEText('{0}<br>{1}</body></html>'.format(sub_list,weekly_msg), 'html')
    msg['Subject'] = 'RDK Mailing weekly subscription digest'
    msg['To'] = key
    print(key)
    #for testing!!!!!!!!!!!!!!!!!!!
    if 'raju_kakkerla' in key:
        print(msg.as_string())
        #p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        #p.communicate(msg.as_string())
        #print(msg.as_string())
    #p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    #p.communicate(msg.as_string())


