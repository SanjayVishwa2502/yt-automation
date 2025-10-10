from pytrends.request import TrendReq
import pandas as pd
import feedparser
import requests
import urllib3
import warnings

# === PATCH: make pytrends compatible with any urllib3 version ===
try:
    Retry = urllib3.util.Retry
    if hasattr(Retry, "allowed_methods") and not hasattr(Retry, "method_whitelist"):
        # new urllib3 ≥2.0 -> alias old name for pytrends
        Retry.method_whitelist = Retry.allowed_methods
    elif hasattr(Retry, "method_whitelist") and not hasattr(Retry, "allowed_methods"):
        # old urllib3 -> just keep existing
        pass
except Exception as e:
    print(f"[urllib3 patch warning] {e}")

warnings.filterwarnings("ignore", category=DeprecationWarning)

# === Initialize pytrends ===
pytrends = TrendReq(hl='en-US', tz=330)

def get_trends_pytrends():
    try:
        df = pytrends.trending_searches(pn='india')
        if df is not None and not df.empty:
            print("\n✅ Top 10 trending searches (via pytrends):")
            print(df.head(10))
            return df.head(10)
    except Exception as e:
        print(f"[pytrends failed] {e}")
    return None

def get_trends_rss():
    try:
        print("\nTrying RSS fallback...")
        # Updated global RSS endpoint (works for most regions)
        url = "https://trends.google.com/trending/rss?geo=IN"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        feed = feedparser.parse(r.content)
        titles = [entry.title for entry in feed.entries[:10]]
        df = pd.DataFrame({'Top_10_Trending_Searches': titles})
        print("\n✅ Top 10 trending searches (via RSS):")
        print(df)
        return df
    except Exception as e:
        print(f"[RSS failed] {e}")
        return None

# === Main ===
trends = get_trends_pytrends()
if trends is None:
    trends = get_trends_rss()

if trends is not None:
    trends.to_csv("top_10_trends.csv", index=False)
    print("\nSaved top 10 trends → top_10_trends.csv")
else:
    print("\n❌ Failed to fetch trends. Try later or use SerpAPI (Google Trends API alternative).")
