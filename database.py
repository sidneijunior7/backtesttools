import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    create_table_sql = """ CREATE TABLE IF NOT EXISTS backtests (
                                id integer PRIMARY KEY,
                                username text NOT NULL,
                                backtest_name text NOT NULL,
                                file_path text NOT NULL
                            ); """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_backtest(conn, backtest):
    sql = ''' INSERT INTO backtests(username, backtest_name, file_path)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, backtest)
    conn.commit()
    return cur.lastrowid

def get_user_backtests(conn, username):
    cur = conn.cursor()
    cur.execute("SELECT * FROM backtests WHERE username=?", (username,))
    rows = cur.fetchall()
    return rows

def delete_backtest(conn, backtest_id):
    sql = 'DELETE FROM backtests WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (backtest_id,))
    conn.commit()
