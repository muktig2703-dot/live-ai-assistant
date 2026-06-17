from tools.search_tool import search_web

print("Searching...")

try:
    results = search_web("latest AI news")

    print("Results found:", len(results))

    for item in results:
        print("\n------------------")
        print("TITLE:", item["title"])
        print("BODY:", item["body"])

except Exception as e:
    print("ERROR:", e)