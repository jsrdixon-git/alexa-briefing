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
