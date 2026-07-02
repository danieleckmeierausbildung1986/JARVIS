import xml.etree.ElementTree as ET

import requests

# Tagesschau-RSS-Feeds, keine Anmeldung/API-Key nötig.
FEEDS = {
    "ausland": "https://www.tagesschau.de/ausland/index~rss2.xml",
    "inland": "https://www.tagesschau.de/inland/index~rss2.xml",
}


def get_news(topic: str = "ausland", limit: int = 5) -> str:
    url = FEEDS.get(topic, FEEDS["ausland"])
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = root.findall("./channel/item")[:limit]
    if not items:
        return "Ich konnte gerade keine Nachrichten abrufen."

    headlines = [item.findtext("title", default="").strip() for item in items]
    return "; ".join(f"{i}. {headline}" for i, headline in enumerate(headlines, start=1))
