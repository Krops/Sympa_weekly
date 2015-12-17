#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pgdb
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import sys
import ldap
import os
import re
import argparse


def parseArgs():
    parser = argparse.ArgumentParser(argument_default=False)

    parser.add_argument('--ldap-server', help='LDAP server', default='ldap://localhost:1389')
    parser.add_argument('--ldap-base', help='Base LDAP scope', default='ou=CCP,dc=ra,dc=ccp,dc=cable,dc=comcast,dc=com')
    parser.add_argument('--user', help='sympa db user', default='sympa_user')
    parser.add_argument('--sympa-password', help='sympa db password', default='')
    parser.add_argument('--db-host', help='sympa db host', default='localhost')
    parser.add_argument('--sympa-url', help='sympa server url', default='https://rdklistmgr.ccp.xcal.tv')

    return parser.parse_args()

def main(args):
    mondbconn = pgdb.connect(user=args.user, password=args.password, database='sympa', host=args.db_host)
    cursor = mondbconn.cursor()
    # ldap initialize
    ldap_client = ldap.initialize(args.ldap_server)
    ldap_base = args.ldap_base
    sql_get_week_names = "select name_list from list_table where status_list='open' and creation_time_list > current_timestamp - interval '12 days'"
    sql_get_user_sub = "select distinct(user_subscriber) from subscriber_table"

    weekly_list = generate_query_list(cursor, sql_get_week_names)
    user_list = generate_query_list(cursor, sql_get_user_sub)
    subscribed_list = generate_sub_dict(cursor, user_list)
    allowedGroups = generate_allowedGroups(weekly_list)

    allgroupusers= {}
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
            sub_list += '<div><label>{0}: </label><a href="{0}/sympa/signoff/{1}">unsub</a></div>'.format(args.sympa_url, name)
        for name in weekly_list:
            if name in allowedGroups:
                for group in allowedGroups[name]:
                    if group not in allgroupusers:
                        try:
                            allgroupusers[group] = ldap_client.search_s(ldap_base, ldap.SCOPE_SUBTREE, '(cn={0})'.format(group))[0][1].get('memberUid',[])
                            print(group)
                        except:
                            continue
                    if user_uid in allgroupusers[group]:
                        print("{0} in {1}".format(key, name))
                        if name in sub_list:
                            weekly_msg += '<div><label>{0}: </label><b>new</b></div>'.format(name)
                            break
                        else:
                            weekly_msg += '<div><label>{0}: </label><a href="{0}/sympa/subscribe/{1}">sub</a></div>'.format(args.sympa_url, name)
                            break
        if weekly_msg==test_wm:
            weekly_msg=''
        msg = MIMEText('{0}<br>{1}</body></html>'.format(sub_list,weekly_msg), 'html')
        msg['Subject'] = 'RDK Mailing weekly subscription digest'
        msg['To'] = key
        print(key)
        if 'ababich' in key:
            print(msg.as_string())
            #p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
            #p.communicate(msg.as_string())
            #print(msg.as_string())
        #p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        #p.communicate(msg.as_string())

def generate_query_list(cursor, sql_query):
    gen_list = []
    try:
        cursor.execute(sql_query)
    except (TypeError, ValueError, pgdb.ProgrammingError, pgdb.InternalError):
        sys.exit(1)
    while (1):
        row = cursor.fetchone()
        if row is None:
            break
        else:
            try:
                gen_list.append(row[0])
            except IndexError:
                sys.exit(1)
    return gen_list

def generate_sub_dict(cursor, user_list):
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
    return subscribed_list

def generate_allowedGroups(weekly_list):
    allowedGroups = {}
    for dir in weekly_list:
        try:
            try:
                file=open('/mnt/sympa/list_data/{0}/config'.format(dir),'r')
            except:
                file=open('/home/sympa/list_data/{0}/config'.format(dir),'r')
                print("{0} in home".format(dir))
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            continue
        text = file.read()
        res_groups = []
        tes_str = re.findall(r'custom_vars\nvalue (.*)\n', text)
        for lst in tes_str:
            groups = [group.strip() for group in lst.split(',')]
            res_groups += groups
            print(groups)
        if len(res_groups)>0:
            allowedGroups[dir]=res_groups
        else:
            continue
        file.close()
    return allowedGroups

if __name__ == "__main__":
    args = parseArgs()
    main(args)
