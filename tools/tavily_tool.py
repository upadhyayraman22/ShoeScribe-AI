import requests
import os
from dotenv import load_dotenv

load_dotenv()

def tavily_search(query):
    url = "https://api.tavily.com/search"

    payload = {
        "api_key": os.getenv("TAVILY_API_KEY"),
        "query": query,
        "search_depth": "basic",
        "max_results": 5
    }

    response = requests.post(url, json=payload)

    return response.json()