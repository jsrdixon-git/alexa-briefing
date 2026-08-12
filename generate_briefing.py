"""
Morning briefing generator — free, no API keys required.

Pulls headlines from public RSS feeds, sorts them into your defined topics
plus a leftover "other news" bucket, and writes an Alexa Flash Briefing
feed.json that Alexa reads out loud each morning.

This is the free/keyword version: no AI summarization, just clean
selection and stitching of real headline text into a short paragraph
per topic. Swapping in an AI summarizer later is a small change (see
the ai_summarize() stub at the bottom).
"""

import json
import feedparser
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# 1. CONFIGURE YOUR TOPICS HERE
#    Each topic has a name and a list of keywords to match against
#    headline + description text (case-insensitive).
# ---------------------------------------------------------------------------
TOPICS = {
    "Crystal Palace and football": [
        "crystal palace", "premier league", "europa league", "football",
    ],
    "Sports betting and horse racing": [
        "betting odds", "horse racing", "cheltenham", "grand national",
    ],
    "Marketing technology": [
        "martech", "marketing technology", "attentive", "klaviyo",
        "email marketing", "sms marketing",
    ],
}

# Feeds to pull from. Add/remove freely — all free, no keys needed.
FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "http://feeds.bbci.co.uk/news/business/rss.xml",
    "http://feeds.bbci.co.uk/news/technology/rss.xml",
]

MAX_ITEMS_PER_TOPIC = 3
MAX_OTHER_ITEMS = 4


def fetch_all_entries():
    """Pull every entry from every configured feed."""
    entries = []
    for url in FEEDS:
        parsed = feedparser.parse(url)
        for e in parsed.entries:
            entries.append({
                "title": e.get("title", ""),
                "summary": e.get("summary", e.get("description", "")),
            })
    return entries


def matches_topic(entry, keywords):
    text = (entry["title"] + " " + entry["summary"]).lower()
    return any(kw.lower() in text for kw in keywords)


def paragraph_for(entries):
    """Stitch a handful of headlines into one readable paragraph."""
    if not entries:
        return None
    parts = []
    for e in entries:
        # Strip any HTML that sometimes sneaks into RSS descriptions
        clean = e["summary"].split("<")[0].strip()
        parts.append(f"{e['title']}. {clean}")
    return " ".join(parts)


def ai_summarize(topic_name, entries):
    """
    OPTIONAL UPGRADE — not used in the free version.
    Swap paragraph_for() for a call to this once you're ready to pay
    the small per-day AI cost for genuine summarization + recommendations.
    Left as a stub so the wiring is obvious later.
    """
    raise NotImplementedError


def build_briefing():
    all_entries = fetch_all_entries()
    used_titles = set()
    segments = []

    for topic_name, keywords in TOPICS.items():
        matches = [e for e in all_entries if matches_topic(e, keywords)]
        matches = matches[:MAX_ITEMS_PER_TOPIC]
        for m in matches:
            used_titles.add(m["title"])
        text = paragraph_for(matches)
        if text:
            segments.append((topic_name, text))

    # "Other news" — leftover entries not already used, capped
    leftovers = [e for e in all_entries if e["title"] not in used_titles]
    other_text = paragraph_for(leftovers[:MAX_OTHER_ITEMS])
    if other_text:
        segments.append(("Other news you might find interesting", other_text))

    return segments


def write_alexa_feed(segments, path="feed.json"):
    """
    Write output in the format Alexa's Flash Briefing skill expects:
    a JSON array of items, each with uid, updateDate, titleText, mainText.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.0Z")
    items = []
    for i, (title, text) in enumerate(segments):
        items.append({
            "uid": f"briefing-{now}-{i}",
            "updateDate": now,
            "titleText": title,
            "mainText": text,
            "redirectionUrl": "",
        })
    with open(path, "w") as f:
        json.dump(items, f, indent=2)
    print(f"Wrote {len(items)} segments to {path}")


if __name__ == "__main__":
    segments = build_briefing()
    write_alexa_feed(segments)
