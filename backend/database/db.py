import sqlite3
import uuid
DB_NAME = "memory.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        is_pinned INTEGER DEFAULT 0,
        is_archived INTEGER DEFAULT 0,
        FOREIGN KEY(user_id)
        REFERENCES users(id)
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
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
)
""")

    conn.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    filename TEXT,
    content TEXT,
    file_path TEXT,
    FOREIGN KEY(chat_id) REFERENCES chats(id)
)
""")
    
    conn.execute("""
CREATE TABLE IF NOT EXISTS shared_chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    share_token TEXT UNIQUE
)
""")

    conn.commit()
    conn.close()


# ------------------------
# CHAT FUNCTIONS
# ------------------------

def create_chat(user_id, title="New Chat"):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
    """
    INSERT INTO chats
    (
        user_id,
        title
    )
    VALUES (?, ?)
    """,
    (
        user_id,
        title
    )
)
    chat_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return chat_id


def get_chats(user_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
        """
        SELECT
            id,
            title,
            is_pinned,
            is_archived
        FROM chats
        WHERE user_id = ?
        ORDER BY is_pinned DESC, id DESC
        """,
        (user_id,)
    )

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


def rename_chat(chat_id, user_id, title):

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
    """
    UPDATE chats
    SET title = ?
    WHERE id = ?
    AND user_id = ?
    """,
    (title, chat_id, user_id)
)

    conn.commit()
    conn.close()


def delete_chat(chat_id, user_id):

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        "DELETE FROM messages WHERE chat_id=?",
        (chat_id,)
    )

    conn.execute(
        "DELETE FROM chats WHERE id=? AND user_id=?",
        (chat_id, user_id)
    )

    conn.commit()
    conn.close()

def toggle_pin(chat_id, user_id):

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        UPDATE chats
        SET is_pinned =
        CASE
            WHEN is_pinned = 1 THEN 0
            ELSE 1
        END
        WHERE id = ?
        AND user_id = ?
    """, (chat_id, user_id))

    conn.commit()
    conn.close()


def toggle_archive(chat_id, user_id):

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        UPDATE chats
        SET is_archived =
        CASE
            WHEN is_archived = 1 THEN 0
            ELSE 1
        END
        WHERE id = ?
        AND user_id = ?
    """, (chat_id, user_id))

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
    content,
    file_path=""
):

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        """
        INSERT INTO documents
        (chat_id, filename, content, file_path)
        VALUES (?, ?, ?, ?)
        """,
        (chat_id, filename, content,file_path)
    )

    conn.commit()
    conn.close()


def get_document(chat_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
        """
        SELECT filename, content, file_path
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
            "content": row[1],
            "file_path": row[2]
        }

    return None

def create_share_link(chat_id):

    token = str(uuid.uuid4())

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        """
        INSERT INTO shared_chats
        (chat_id, share_token)
        VALUES (?, ?)
        """,
        (chat_id, token)
    )

    conn.commit()
    conn.close()

    return token

def get_shared_chat(token):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
        """
        SELECT chat_id
        FROM shared_chats
        WHERE share_token=?
        """,
        (token,)
    )

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return row[0]
#-------------------------------------
#--------USER AUTHENTICATION----------
#-------------------------------------
def create_user(
    name,
    email,
    password_hash
):

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        """
        INSERT INTO users
        (
            name,
            email,
            password_hash
        )
        VALUES (?, ?, ?)
        """,
        (
            name,
            email,
            password_hash
        )
    )

    conn.commit()
    conn.close()
    
def get_user_by_email(email):

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    conn.close()

    return dict(user) if user else None

def chat_belongs_to_user(
    chat_id,
    user_id
):

    conn = sqlite3.connect(DB_NAME)

    chat = conn.execute(
        """
        SELECT id
        FROM chats
        WHERE id = ?
        AND user_id = ?
        """,
        (
            chat_id,
            user_id
        )
    ).fetchone()

    conn.close()

    return chat is not None
