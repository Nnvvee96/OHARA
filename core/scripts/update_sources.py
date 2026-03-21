#!/usr/bin/env python3
"""
Update wizard signal_sources to use new Adapter format.
Run once on VPS after git pull.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import db

SOURCES = {
    "aria": [
        {"type": "hackernews"},
        {"type": "rss", "url": "https://hnrss.org/newest?points=50", "name": "hn-top50", "tier": "aggregator", "independence": 0.6},
        {"type": "reddit", "subreddits": ["MachineLearning", "LocalLLaMA", "artificial"]},
    ],
    "marcus": [
        {"type": "hackernews"},
        {"type": "rss", "url": "https://hnrss.org/newest?points=30", "name": "hn-top30", "tier": "aggregator", "independence": 0.6},
        {"type": "reddit", "subreddits": ["programming", "softwarearchitecture", "devops", "ExperiencedDevs"]},
    ],
    "nova": [
        {"type": "hackernews"},
        {"type": "rss", "url": "https://hnrss.org/newest?points=30", "name": "hn-top30", "tier": "aggregator", "independence": 0.6},
        {"type": "reddit", "subreddits": ["SaaS", "indiehackers", "webdev", "startups"]},
    ],
    "sterling": [
        {"type": "hackernews"},
        {"type": "rss", "url": "https://hnrss.org/newest?points=50", "name": "hn-top50", "tier": "aggregator", "independence": 0.6},
        {"type": "reddit", "subreddits": ["investing", "SecurityAnalysis", "stocks"]},
    ],
    "reina": [
        {"type": "hackernews"},
        {"type": "rss", "url": "https://hnrss.org/newest?points=30", "name": "hn-top30", "tier": "aggregator", "independence": 0.6},
        {"type": "reddit", "subreddits": ["marketing", "SEO", "growth_hacking", "entrepreneur"]},
    ],
}

conn = db.governance_db()
for short_name, sources in SOURCES.items():
    conn.execute(
        "UPDATE wizards SET signal_sources=? WHERE short_name=?",
        (json.dumps(sources), short_name)
    )
    print(f"  Updated: {short_name}")
conn.commit()
conn.close()
print("Done — all wizard sources updated to adapter format")
