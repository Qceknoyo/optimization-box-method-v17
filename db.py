import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host":     "127.0.0.1",
    "port":     5432,
    "dbname":   "mo_chp",       # имя твоей БД
    "user":     "qceknoyo",     # твой юзер
    "password": "2108" # твой пароль
    
}

_conn = None

def get_db_connection():
    global _conn

    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(
        **DB_CONFIG,
        connect_timeout=3
    )
    
    return _conn

def get_user(username):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cur.fetchone()
    cur.close()

    return user

def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM tasks ORDER BY id')
    tasks = cur.fetchall()
    cur.close()

    return tasks

def get_methods():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM methods ORDER BY id')
    methods = cur.fetchall()
    cur.close()

    return methods

def get_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM users ORDER BY id')
    users = cur.fetchall()
    cur.close()

    return users
