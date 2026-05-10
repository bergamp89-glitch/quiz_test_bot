import sqlite3
from datetime import datetime


DB_NAME = "quiz.db"


# Botdagi fanlar ro‘yxati
SUBJECT_NAMES = {
    "iqtisodiyot": "Iqtisodiyot",
    "dm": "DM",
    "mikro_makro": "Mikro-Makro iqtisodiyot",
    "moliya": "Moliya",
    "statistika": "Statistika",
    "innovatsion_iqtisodiyot": "Innovatsion iqtisodiyot",
    "menejment_marketing": "Menejment-Marketing",
}


def connect_db():
    """
    SQLite bazaga ulanadi.
    row_factory orqali natijalarni dictga o‘xshash ko‘rinishda olish mumkin.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Kerakli jadvallarni yaratadi:
    - questions: test savollari
    - results: foydalanuvchi natijalari
    - users: bot foydalanuvchilari
    """
    conn = connect_db()
    cursor = conn.cursor()

    # Test savollari jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_key TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT
        )
    """)

    # Natijalar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT,
            username TEXT,
            subject_key TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            total INTEGER NOT NULL,
            correct_count INTEGER NOT NULL,
            wrong_count INTEGER NOT NULL,
            percent REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            full_name TEXT,
            username TEXT,
            first_seen TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, full_name, username):
    """
    /start bosgan foydalanuvchini users jadvaliga qo‘shadi.
    Agar oldin mavjud bo‘lsa, ismi va username yangilanadi.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (
            user_id, full_name, username, first_seen
        )
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        full_name,
        username,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    cursor.execute("""
        UPDATE users
        SET full_name = ?, username = ?
        WHERE user_id = ?
    """, (
        full_name,
        username,
        user_id
    ))

    conn.commit()
    conn.close()


def get_random_questions(subject_key: str, limit: int):
    """
    Tanlangan fandan random savollarni oladi.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM questions
        WHERE subject_key = ?
        ORDER BY RANDOM()
        LIMIT ?
    """, (subject_key, limit))

    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return questions


def get_question_count(subject_key: str):
    """
    Bitta fan bo‘yicha savollar sonini qaytaradi.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM questions
        WHERE subject_key = ?
    """, (subject_key,))

    count = cursor.fetchone()["count"]
    conn.close()

    return count


def save_result(
    user_id,
    full_name,
    username,
    subject_key,
    total,
    correct_count,
    wrong_count,
    percent
):
    """
    Test natijasini bazaga saqlaydi.
    """
    conn = connect_db()
    cursor = conn.cursor()

    subject_name = SUBJECT_NAMES.get(subject_key, subject_key)

    cursor.execute("""
        INSERT INTO results (
            user_id,
            full_name,
            username,
            subject_key,
            subject_name,
            total,
            correct_count,
            wrong_count,
            percent,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        full_name,
        username,
        subject_key,
        subject_name,
        total,
        correct_count,
        wrong_count,
        percent,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_user_results(user_id, limit=5):
    """
    Foydalanuvchining oxirgi natijalarini qaytaradi.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM results
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return results


def get_top_results(limit=10):
    """
    Umumiy reyting uchun eng yaxshi natijalarni qaytaradi.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM results
        ORDER BY percent DESC, correct_count DESC, id ASC
        LIMIT ?
    """, (limit,))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return results


def get_users_count():
    """
    Botdan foydalangan jami foydalanuvchilar soni.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM users")
    count = cursor.fetchone()["count"]

    conn.close()
    return count


def get_results_count():
    """
    Jami ishlangan testlar soni.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM results")
    count = cursor.fetchone()["count"]

    conn.close()
    return count


def get_questions_count():
    """
    Bazadagi jami test savollari soni.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM questions")
    count = cursor.fetchone()["count"]

    conn.close()
    return count


def get_subjects_statistics():
    """
    Har bir fan bo‘yicha savollar sonini qaytaradi.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject_name, COUNT(*) AS count
        FROM questions
        GROUP BY subject_key, subject_name
        ORDER BY subject_name
    """)

    stats = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return stats