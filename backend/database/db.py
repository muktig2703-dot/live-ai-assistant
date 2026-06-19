import sqlite3

DB_NAME = "memory.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        is_pinned INTEGER DEFAULT 0,
        is_archived INTEGER DEFAULT 0
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY(chat_id) REFERENCES chats(id)
    )
    """)

    conn.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    filename TEXT,
    content TEXT,
    FOREIGN KEY(chat_id) REFERENCES chats(id)
)
""")

    conn.commit()
    conn.close()


# ------------------------
# CHAT FUNCTIONS
# ------------------------

def create_chat(title="New Chat"):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
        "INSERT INTO chats (title) VALUES (?)",
        (title,)
    )

    chat_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return chat_id


def get_chats():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute("""
    SELECT id, title, is_pinned, is_archived
    FROM chats
    ORDER BY is_pinned DESC, id DESC
    """)

    chats = []

    for row in cursor:
        chats.append({
            "id": row[0],
            "title": row[1],
            "is_pinned": row[2],
            "is_archived": row[3]
        })

    conn.close()

    return chats


def rename_chat(chat_id, title):

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        "UPDATE chats SET title=? WHERE id=?",
        (title, chat_id)
    )

    conn.commit()
    conn.close()


def delete_chat(chat_id):

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        "DELETE FROM messages WHERE chat_id=?",
        (chat_id,)
    )

    conn.execute(
        "DELETE FROM chats WHERE id=?",
        (chat_id,)
    )

    conn.commit()
    conn.close()

def toggle_pin(chat_id):

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        UPDATE chats
        SET is_pinned =
        CASE
            WHEN is_pinned = 1 THEN 0
            ELSE 1
        END
        WHERE id = ?
    """, (chat_id,))

    conn.commit()
    conn.close()


def toggle_archive(chat_id):

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        UPDATE chats
        SET is_archived =
        CASE
            WHEN is_archived = 1 THEN 0
            ELSE 1
        END
        WHERE id = ?
    """, (chat_id,))

    conn.commit()
    conn.close()

    
# ------------------------
# MESSAGE FUNCTIONS
# ------------------------

def save_message(chat_id, role, content):

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        """
        INSERT INTO messages
        (chat_id, role, content)
        VALUES (?, ?, ?)
        """,
        (chat_id, role, content)
    )

    conn.commit()
    conn.close()


def get_messages(chat_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
        """
        SELECT role, content
        FROM messages
        WHERE chat_id=?
        ORDER BY id
        """,
        (chat_id,)
    )

    messages = []

    for row in cursor:
        messages.append({
            "role": row[0],
            "content": row[1]
        })

    conn.close()

    return messages

# ------------------------
# DOCUMENT FUNCTIONS
# ------------------------

def save_document(
    chat_id,
    filename,
    content
):

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        """
        INSERT INTO documents
        (chat_id, filename, content)
        VALUES (?, ?, ?)
        """,
        (chat_id, filename, content)
    )

    conn.commit()
    conn.close()


def get_document(chat_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
        """
        SELECT filename, content
        FROM documents
        WHERE chat_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (chat_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:

        return {
            "filename": row[0],
            "content": row[1]
        }

    return None