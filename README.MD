1. Install dependencies for python-postgres connection install PyGreSQL:

    sudo yum install PyGreSQL

or

    sudo aptitude install python-pygresql

or

    sudo pip install PyGreSQL


2. Configure RDK Mailing weekly subscription digest (send_weekly_reborn.py)
Before use change default args field for connection to DB and ldap:

    python2.7 send_weekly_reborn.py -h

3. Than copy send_weekly.py to crone script location.

    sudo chmod +x send_weekly_reborn.py

    crontab -e

(press 'i' for insert)
and insert:

    0 23 * * 0 /location/send_weekly.py

(save in vi Esc + :wq)
Show cron changes:

    cronetab -l
