import requests

def get_news_urls(api_key, query="India news", page_size=10):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "language": "en",
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "ok" and data.get("articles"):
        return [article.get("url") for article in data["articles"] if article.get("url")]
    else:
        return []

API_KEY = "e39b42bd2c4843118a5de396ee7eacce"
urls = get_news_urls(API_KEY, query="India news", page_size=5)
print(urls)
