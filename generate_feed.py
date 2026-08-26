#!/usr/bin/env python3
"""
Generate an RSS 2.0 feed for History of Education Review
from Crossref metadata.

Journal:
- History of Education Review
- eISSN: 2054-5649
"""

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

ISSN = "2054-5649"
ROWS = 50
OUTPUT = Path(__file__).with_name("feed.xml")

CROSSREF_API = f"https://api.crossref.org/journals/{ISSN}/works"
JOURNAL_URL = "https://www.emerald.com/insight/publication/issn/0819-8691"


def text_from(value, default=""):
    if isinstance(value, list):
        return value[0] if value else default
    return value or default


def first_date(item):
    """
    Prefer online/published/print dates, then created timestamp.
    Returns an aware UTC datetime.
    """
    for key in ("published-online", "published", "published-print", "issued"):
        part = item.get(key, {})
        date_parts = part.get("date-parts") if isinstance(part, dict) else None
        if date_parts and date_parts[0]:
            p = date_parts[0]
            year = int(p[0])
            month = int(p[1]) if len(p) > 1 else 1
            day = int(p[2]) if len(p) > 2 else 1
            return datetime(year, month, day, tzinfo=timezone.utc)

    created = item.get("created", {})
    if isinstance(created, dict) and created.get("timestamp"):
        return datetime.fromtimestamp(created["timestamp"] / 1000, tz=timezone.utc)

    return datetime.now(timezone.utc)


def author_string(item):
    authors = []
    for a in item.get("author", []) or []:
        given = (a.get("given") or "").strip()
        family = (a.get("family") or "").strip()
        name = " ".join(x for x in (given, family) if x)
        if name:
            authors.append(name)
    return ", ".join(authors)


def fetch_items():
    params = {
        "rows": ROWS,
        "sort": "published",
        "order": "desc",
        "select": "DOI,title,author,published,published-online,published-print,issued,created,URL,abstract,type",
    }
    url = CROSSREF_API + "?" + urllib.parse.urlencode(params)

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "history-of-education-review-rss/1.0 "
                          "(personal RSS feed for Zotero)"
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)

    return data["message"]["items"]


def build_feed(items):
    rss = Element("rss", {"version": "2.0"})
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "History of Education Review"
    SubElement(channel, "link").text = JOURNAL_URL
    SubElement(channel, "description").text = (
        "Recent articles from History of Education Review "
        "(Crossref metadata; eISSN 2054-5649)."
    )
    SubElement(channel, "language").text = "en"
    SubElement(channel, "lastBuildDate").text = format_datetime(
        datetime.now(timezone.utc)
    )
    SubElement(channel, "generator").text = "generate_feed.py / Crossref REST API"

    for work in items:
        doi = (work.get("DOI") or "").strip()
        title = text_from(work.get("title"), "Untitled article").strip()
        url = (work.get("URL") or "").strip()
        if not url and doi:
            url = f"https://doi.org/{doi}"

        item = SubElement(channel, "item")
        SubElement(item, "title").text = title
        SubElement(item, "link").text = url

        guid = SubElement(item, "guid")
        guid.set("isPermaLink", "false")
        guid.text = doi or url or title

        pub_date = first_date(work)
        SubElement(item, "pubDate").text = format_datetime(pub_date)

        authors = author_string(work)
        if authors:
            SubElement(item, "author").text = authors

        description_parts = []
        if authors:
            description_parts.append(f"Authors: {authors}")
        if doi:
            description_parts.append(f"DOI: {doi}")
        abstract = (work.get("abstract") or "").strip()
        if abstract:
            description_parts.append(abstract)

        if description_parts:
            SubElement(item, "description").text = "\n\n".join(description_parts)

    tree = ElementTree(rss)
    try:
        ElementTree.indent(tree, space="  ")
    except AttributeError:
        pass

    tree.write(OUTPUT, encoding="utf-8", xml_declaration=True)


def main():
    items = fetch_items()
    build_feed(items)
    print(f"Wrote {OUTPUT} with {len(items)} items.")


if __name__ == "__main__":
    main()
