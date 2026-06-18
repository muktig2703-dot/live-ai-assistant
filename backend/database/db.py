import sqlite3

DB_NAME = "memory.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def save_message(role, content):
    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        "INSERT INTO messages (role, content) VALUES (?, ?)",
        (role, content)
    )

    conn.commit()
    conn.close()


def get_messages():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
        "SELECT role, content FROM messages ORDER BY id"
    )

    messages = []

    for row in cursor:
        messages.append({
            "role": row[0],
            "content": row[1]
        })

    conn.close()

    return messages