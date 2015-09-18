1. Install dependecies
For python-postgres connection install PyGreSQL:

    sudo yum install PyGreSQL
or
    sudo aptitude install python-pygresql
or
    sudo pip install PyGreSQL

For test_speed_sql_weekly.py we need install kernprof

    sudo pip install line_profiler

2. Modificate Sympa DB
That script's adding new column (creation_time_list) into sympa list_table and it's inserting default current date into new column for new
rows and creation date for old rows.
Before use change this field for connection to DB in update_sympa_db.py:

    mcedit update_sympa_db.py

    ///mondbconn = pgdb.connect(user='postgres', password = '46KNVgw274', database = 'sympa')

Then (don't use it twice!!):

    python update_sympa_db.py

3. Test SQL speed of send_weekly.py script
Use:

    kernprof -l -v test_speed_sql_weekly.py

4. Configure RDK Mailing weekly subscription digest (send_weekly.py)
Before use change this field for connection to DB in update_sympa_db.py:

    mcedit send_weekly.py

    ///mondbconn = pgdb.connect(user='postgres', password = '46KNVgw274', database = 'sympa')

Than copy send_weekly.py to crone script location.

    sudo chmod +x send_weekly.py

    crontab -e

(press 'i' for insert)
and insert:

    0 23 * * 0 /location/send_weekly.py

(save in vi Esc + :wq)
Show cron changes:

    cronetab -l
