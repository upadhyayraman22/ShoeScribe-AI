from tools.tavily_tool import tavily_search

def research_agent(product_name, category):
    query = f"{product_name} {category} features benefits"

    results = tavily_search(query)

    summaries = []

    for r in results.get("results", []):
        summaries.append(r.get("content", ""))

    return {
        "query": query,
        "summary": summaries
    }