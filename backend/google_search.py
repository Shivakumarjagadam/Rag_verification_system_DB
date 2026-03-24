import requests
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID


def google_search(query):

    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "dateRestrict": "m3",
        "num": 5
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []

    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("link"),
            "snippet": item.get("snippet")
        })

    return results