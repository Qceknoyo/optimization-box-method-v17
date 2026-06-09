import sqlite3
import os
import sys, os

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # папка рядом с exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # папка рядом со скриптом

DB_PATH = os.path.join(BASE_DIR, "mo_chp.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # чтобы обращаться по имени колонки как в psycopg2
    return conn

def _init_db():
    """Создаёт таблицы и начальные данные если БД ещё не существует"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role     TEXT NOT NULL DEFAULT 'researcher'
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            is_active   INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS methods (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            description TEXT
        );
    """)
    # Начальные данные (только если таблицы пустые)
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.executescript("""
            INSERT INTO users (username, password, role) VALUES ('admin', 'admin', 'admin');
            INSERT INTO users (username, password, role) VALUES ('user', 'user', 'researcher');
            INSERT INTO tasks (title, description) VALUES ('Вариант №17', 'Оптимизация себестоимости химического процесса');
            INSERT INTO methods (name, description) VALUES ('Метод Бокса', 'Метод деформируемого комплекса (метод Бокса) для условной оптимизации');
            INSERT INTO methods (name, description) VALUES ('Метод координатного спуска', 'Поочерёдная оптимизация по каждой переменной при фиксированных остальных');
        """)
    conn.commit()
    cur.close()
    conn.close()

def get_user(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks ORDER BY id')
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return tasks

def get_methods():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM methods ORDER BY id')
    methods = cur.fetchall()
    cur.close()
    conn.close()
    return methods

def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users ORDER BY id')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

# Инициализируем БД при импорте
_init_db()