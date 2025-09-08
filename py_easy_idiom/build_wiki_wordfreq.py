#!/usr/bin/env python3
"""
build_wiki_wordfreq.py

Fetch random English Wikipedia articles (via MediaWiki API),
build a corpus, compute word frequencies, and save top N words to CSV.

Requirements:
    pip install requests tqdm

Usage:
    python build_wiki_wordfreq.py
"""

import requests
import time
import re
import csv
import sys
from collections import Counter
from tqdm import tqdm
from random import uniform

API_ENDPOINT = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "WordFreqBot/1.0 (drevondorian@example.com) Python/requests"

# --- Configurable parameters ---
TARGET_WORDS = 2_000_000   # stop when we've collected this many words (set to None to ignore)
MAX_ARTICLES = 20000       # max number of articles to request (safety cap)
TOP_N = 10000              # how many top words to write to CSV
OUT_CSV = "wiki_wordfreq_top{}.csv".format(TOP_N)
MIN_ARTICLE_WORDS = 50     # ignore extremely short extracts
SLEEP_MIN = 0.5            # seconds (politeness)
SLEEP_MAX = 1.5            # seconds (politeness)
# --------------------------------

HEADERS = {"User-Agent": USER_AGENT}

def get_random_page_title(session):
    """
    Use action=query&list=random to get a random page title in main namespace.
    """
    params = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnnamespace": 0,
        "rnlimit": 1
    }
    r = session.get(API_ENDPOINT, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    title = data["query"]["random"][0]["title"]
    return title

def fetch_extract_for_title(session, title):
    """
    Use prop=extracts&explaintext to fetch plaintext extract for a given title.
    """
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": 1,
        "titles": title,
        "exlimit": 1,
    }
    r = session.get(API_ENDPOINT, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return ""
    # pages keys are pageids (strings)
    page = next(iter(pages.values()))
    extract = page.get("extract", "") or ""
    return extract

def tokenize(text):
    WORD_RE = re.compile(r"\b[a-z']+\b", re.IGNORECASE)  # basic tokenizer: letters and apostrophes
    return [w.lower() for w in WORD_RE.findall(text)]

def main():
    print("Starting: fetching random Wikipedia articles and building word frequencies.")
    print(f"Target words: {TARGET_WORDS}, Max articles: {MAX_ARTICLES}, Top N: {TOP_N}")
    session = requests.Session()

    counter = Counter()
    total_words = 0
    articles_count = 0

    pbar = tqdm(total=(TARGET_WORDS or MAX_ARTICLES), unit="words" if TARGET_WORDS else "articles")
    try:
        while True:
            if MAX_ARTICLES and articles_count >= MAX_ARTICLES:
                break
            # get a random title
            try:
                title = get_random_page_title(session)
            except Exception as e:
                print(f"Warning: failed to get random page title: {e}", file=sys.stderr)
                time.sleep(2)
                continue

            # fetch extract
            try:
                extract = fetch_extract_for_title(session, title)
            except Exception as e:
                print(f"Warning: failed to fetch extract for '{title}': {e}", file=sys.stderr)
                time.sleep(2)
                continue

            if not extract:
                # sometimes unavailable; skip
                continue

            tokens = tokenize(extract)
            if len(tokens) < MIN_ARTICLE_WORDS:
                # skip very short pages (disambiguation, stub, etc.)
                continue

            counter.update(tokens)
            total_words += len(tokens)
            articles_count += 1

            # update progress bar
            if TARGET_WORDS:
                pbar.total = TARGET_WORDS
                pbar.update(min(len(tokens), max(0, TARGET_WORDS - pbar.n)))
            else:
                pbar.update(1)

            # polite pause
            time.sleep(uniform(SLEEP_MIN, SLEEP_MAX))

            # stopping condition
            if TARGET_WORDS and total_words >= TARGET_WORDS:
                break
    except KeyboardInterrupt:
        print("\nInterrupted by user - will save progress so far.")
    finally:
        pbar.close()

    if total_words == 0:
        print("No words collected. Exiting.")
        return

    # prepare CSV: top TOP_N words by count
    top = counter.most_common(TOP_N)
    # compute normalized frequency per million words
    norm_factor = 1_000_000.0 / total_words
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "word", "count", "freq_per_million"])
        for idx, (w, c) in enumerate(top, start=1):
            writer.writerow([idx, w, c, round(c * norm_factor, 6)])

    print(f"Collected {total_words:,} words from {articles_count} articles.")
    print(f"Wrote top {len(top)} words to {OUT_CSV}")

if __name__ == "__main__":
    main()
