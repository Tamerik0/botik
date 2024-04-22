import os.path
import sqlite3

init = not os.path.exists('db.sqlite')
con = sqlite3.Connection('db.sqlite')
cur = con.cursor()


def init_db():
    cur.execute(
        """CREATE TABLE Messages (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user,
            role,
            content
        );""")



if init:
    init_db()
