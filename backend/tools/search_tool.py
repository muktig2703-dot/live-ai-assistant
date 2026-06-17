from ddgs import DDGS

def search_web(query):
    results = []

    with DDGS() as ddgs:
        search_results = ddgs.text(query, max_results=5)

        for result in search_results:
            results.append({
                "title": result.get("title"),
                "body": result.get("body"),
                "link": result.get("href")
            })

    return results