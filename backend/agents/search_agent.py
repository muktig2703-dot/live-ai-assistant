def needs_search(user_message):

    search_keywords = [
        "latest",
        "today",
        "news",
        "current",
        "recent",
        "yesterday",
        "update",
        "updates",
        "who won",
        "weather",
        "stock",
        "price"
    ]

    user_message = user_message.lower()

    for keyword in search_keywords:
        if keyword in user_message:
            return True

    return False