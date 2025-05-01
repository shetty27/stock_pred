import requests

def get_news_from_upstox(symbol: str):
    url = f"https://api.upstox.com/news/{symbol}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("articles", [])
    else:
        print(f"⚠️ Upstox News API Error {response.status_code} for {symbol}")
        return []

def get_combined_news(symbol: str):
    return get_news_from_upstox(symbol)
