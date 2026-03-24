def build_context(search_results):

    context = ""

    for i, r in enumerate(search_results):

        context += f"""
Source {i+1}
Title: {r['title']}
Snippet: {r['snippet']}
URL: {r['url']}

"""

    return context