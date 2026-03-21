"""
OHARA — Source Adapters
Prinzip: API or Feed first. Browser second. Scraping last.

Jede Quelle hat einen dedizierten Adapter.
Adapters geben eine Liste von SourceItem zurück.
Scout konsumiert Adapters — nie direkte HTTP-Calls im Scout.
"""

import json
import time
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional

# ============================================================
# SOURCE ITEM — was ein Adapter zurückgibt
# ============================================================

@dataclass
class SourceItem:
    url: str
    title: str
    text: str               # Vorverarbeiteter Text für LLM
    source_name: str        # z.B. "hackernews", "reddit/r/SaaS"
    source_tier: str        # primary / secondary / aggregator / social
    independence_score: float  # 0.0-1.0
    published_at: Optional[str] = None

# ============================================================
# BASE ADAPTER
# ============================================================

class BaseAdapter:
    def fetch(self, limit: int = 10) -> list[SourceItem]:
        raise NotImplementedError

    def _get(self, url: str, headers: dict = None, timeout: int = 10) -> bytes:
        req = urllib.request.Request(
            url,
            headers=headers or {"User-Agent": "OHARA/1.0 knowledge-librarian"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()

# ============================================================
# HACKERNEWS ADAPTER — kein Auth, stabil, Phase 1
# ============================================================

class HackerNewsAdapter(BaseAdapter):
    """
    HackerNews via Firebase API.
    Kein Auth nötig. Sehr stabil. Ideal für Phase 1.
    """
    BASE = "https://hacker-news.firebaseio.com/v0"

    def fetch(self, limit: int = 15) -> list[SourceItem]:
        results = []
        try:
            # Top stories
            data = self._get(f"{self.BASE}/topstories.json")
            ids = json.loads(data)[:limit * 2]  # Mehr holen als nötig

            for sid in ids:
                if len(results) >= limit:
                    break
                try:
                    item_data = self._get(f"{self.BASE}/item/{sid}.json")
                    item = json.loads(item_data)
                    if not item or item.get("type") != "story":
                        continue
                    if not item.get("title"):
                        continue

                    text = item.get("title", "")
                    if item.get("text"):
                        text += "\n\n" + item["text"]

                    results.append(SourceItem(
                        url=item.get("url") or f"https://news.ycombinator.com/item?id={sid}",
                        title=item.get("title", ""),
                        text=text[:6000],
                        source_name="hackernews",
                        source_tier="aggregator",
                        independence_score=0.6,
                        published_at=str(item.get("time", "")),
                    ))
                    time.sleep(0.15)
                except Exception:
                    continue

        except Exception as e:
            print(f"  [HackerNews] Fetch failed: {e}")

        return results

# ============================================================
# RSS ADAPTER — öffentliche Feeds, Phase 1
# ============================================================

class RSSAdapter(BaseAdapter):
    """
    RSS/Atom Feed Adapter.
    Funktioniert für: HN RSS, Blogs, Substack, GitHub Releases etc.
    """

    def __init__(self, feed_url: str, source_name: str,
                 source_tier: str = "secondary",
                 independence_score: float = 0.5):
        self.feed_url = feed_url
        self.source_name = source_name
        self.source_tier = source_tier
        self.independence_score = independence_score

    def fetch(self, limit: int = 15) -> list[SourceItem]:
        results = []
        try:
            data = self._get(self.feed_url)
            root = ET.fromstring(data)

            # Handle both RSS and Atom
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = root.findall(".//item") or root.findall(".//atom:entry", ns)

            for item in items[:limit]:
                try:
                    # RSS
                    title = item.findtext("title") or item.findtext("atom:title", namespaces=ns) or ""
                    link = item.findtext("link") or item.findtext("atom:link", namespaces=ns) or ""
                    desc = item.findtext("description") or item.findtext("atom:summary", namespaces=ns) or ""
                    pub = item.findtext("pubDate") or item.findtext("atom:published", namespaces=ns) or ""

                    if not title:
                        continue

                    text = title
                    if desc:
                        # Strip basic HTML tags
                        import re
                        clean = re.sub(r"<[^>]+>", " ", desc)
                        clean = re.sub(r"\s+", " ", clean).strip()
                        text += "\n\n" + clean[:3000]

                    results.append(SourceItem(
                        url=link,
                        title=title,
                        text=text[:6000],
                        source_name=self.source_name,
                        source_tier=self.source_tier,
                        independence_score=self.independence_score,
                        published_at=pub,
                    ))
                except Exception:
                    continue

        except Exception as e:
            print(f"  [RSS:{self.source_name}] Fetch failed: {e}")

        return results

# ============================================================
# REDDIT ADAPTER — Phase 2 (benötigt API credentials)
# ============================================================

class RedditAdapter(BaseAdapter):
    """
    Reddit via offizieller API.
    Benötigt: client_id, client_secret, user_agent
    Setup: reddit.com/prefs/apps → create app → script type

    Phase 2 — noch nicht aktiv.
    """

    def __init__(self, client_id: str, client_secret: str,
                 subreddits: list[str], user_agent: str = "OHARA/1.0"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.subreddits = subreddits
        self.user_agent = user_agent
        self._token = None

    def _get_token(self) -> str:
        import base64
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        req = urllib.request.Request(
            "https://www.reddit.com/api/v1/access_token",
            data=b"grant_type=client_credentials",
            headers={
                "Authorization": f"Basic {credentials}",
                "User-Agent": self.user_agent,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        return data["access_token"]

    def fetch(self, limit: int = 15) -> list[SourceItem]:
        if not self._token:
            try:
                self._token = self._get_token()
            except Exception as e:
                print(f"  [Reddit] Auth failed: {e}")
                return []

        results = []
        per_sub = max(5, limit // len(self.subreddits))

        for sub in self.subreddits:
            try:
                req = urllib.request.Request(
                    f"https://oauth.reddit.com/r/{sub}/hot.json?limit={per_sub}",
                    headers={
                        "Authorization": f"Bearer {self._token}",
                        "User-Agent": self.user_agent,
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read())

                posts = data.get("data", {}).get("children", [])
                for post in posts:
                    d = post.get("data", {})
                    score = d.get("score", 0)
                    if score < 5:  # Min score filter
                        continue

                    text = d.get("title", "")
                    if d.get("selftext"):
                        text += "\n\n" + d["selftext"][:3000]

                    results.append(SourceItem(
                        url=f"https://reddit.com{d.get('permalink', '')}",
                        title=d.get("title", ""),
                        text=text[:6000],
                        source_name=f"reddit/r/{sub}",
                        source_tier="social",
                        independence_score=0.4,
                        published_at=str(d.get("created_utc", "")),
                    ))
                time.sleep(1.0)  # Reddit rate limit

            except Exception as e:
                print(f"  [Reddit/r/{sub}] Failed: {e}")
                self._token = None  # Reset token on error
                continue

        return results[:limit]

# ============================================================
# X (TWITTER) ADAPTER — Phase 2 (benötigt API credentials)
# ============================================================

class XAdapter(BaseAdapter):
    """
    X via offizieller API v2.
    Benötigt: bearer_token (App-only) oder OAuth2 (für Bookmarks)
    Setup: console.x.com

    Zwei Modi:
    - search: thematische Suche via Queries
    - bookmarks: deine eigenen Bookmarks (User Context Auth)

    Phase 2 — noch nicht aktiv.
    """

    def __init__(self, bearer_token: str, queries: list[str] = None,
                 mode: str = "search"):
        self.bearer_token = bearer_token
        self.queries = queries or []
        self.mode = mode  # "search" or "bookmarks"

    def fetch(self, limit: int = 20) -> list[SourceItem]:
        results = []
        per_query = max(5, limit // max(len(self.queries), 1))

        for query in self.queries:
            try:
                encoded = urllib.parse.quote(query)
                url = (f"https://api.twitter.com/2/tweets/search/recent"
                       f"?query={encoded}&max_results={per_query}"
                       f"&tweet.fields=created_at,text,author_id")
                req = urllib.request.Request(
                    url,
                    headers={"Authorization": f"Bearer {self.bearer_token}"}
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read())

                for tweet in data.get("data", []):
                    results.append(SourceItem(
                        url=f"https://x.com/i/web/status/{tweet['id']}",
                        title=tweet["text"][:100],
                        text=tweet["text"],
                        source_name="x/search",
                        source_tier="social",
                        independence_score=0.35,
                        published_at=tweet.get("created_at"),
                    ))
                time.sleep(1.0)

            except Exception as e:
                print(f"  [X/search] Failed: {e}")

        return results[:limit]

# ============================================================
# ADAPTER FACTORY — pro Wizard die richtigen Adapters laden
# ============================================================

def get_adapters_for_wizard(wizard: dict) -> list[BaseAdapter]:
    """
    Gibt die richtigen Adapter für einen Wizard zurück.
    Basiert auf wizard.signal_sources config.
    Phase 1: nur HackerNews + RSS.
    Phase 2+: Reddit + X wenn credentials vorhanden.
    """
    import os
    adapters = []
    sources = json.loads(wizard.get("signal_sources", "[]"))

    for src in sources:
        src_type = src.get("type", "")

        if src_type == "hackernews":
            adapters.append(HackerNewsAdapter())

        elif src_type == "rss":
            url = src.get("url", "")
            if url:
                adapters.append(RSSAdapter(
                    feed_url=url,
                    source_name=src.get("name", url[:40]),
                    source_tier=src.get("tier", "secondary"),
                    independence_score=src.get("independence", 0.5),
                ))

        elif src_type == "reddit":
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            if client_id and client_secret:
                subreddits = src.get("subreddits", [])
                if subreddits:
                    adapters.append(RedditAdapter(
                        client_id=client_id,
                        client_secret=client_secret,
                        subreddits=subreddits,
                    ))
            else:
                print(f"  [Reddit] Skipped — no credentials in .env")

        elif src_type == "x":
            bearer = os.getenv("X_BEARER_TOKEN")
            if bearer:
                queries = src.get("queries", [])
                adapters.append(XAdapter(
                    bearer_token=bearer,
                    queries=queries,
                    mode=src.get("mode", "search"),
                ))
            else:
                print(f"  [X] Skipped — no X_BEARER_TOKEN in .env")

    # Fallback: immer HackerNews wenn keine anderen Quellen
    if not adapters:
        print(f"  [Adapters] No sources configured — falling back to HackerNews")
        adapters.append(HackerNewsAdapter())

    return adapters
