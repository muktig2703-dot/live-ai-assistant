from database.db import (
    init_db,
    save_message,
    get_messages
)

init_db()

save_message("user", "Hello")
save_message("assistant", "Hi there")

messages = get_messages()

print(messages)