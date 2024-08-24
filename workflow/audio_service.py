import logging
import time
from datetime import datetime
from io import BytesIO

import feedparser
import requests

from workflow.models import Brief


def fetch_audio_details_from_rss(rss_url: str) -> Brief:
    if not rss_url:
        raise ValueError(f"Invalid rss_url: '{rss_url}'")
    logging.info("Fetching audio info")
    feed = feedparser.parse(rss_url)
    latest_entry = feed.entries[0]
    guid = latest_entry["guid"]
    title = latest_entry["title"]
    published_time = datetime.fromtimestamp(
        time.mktime(latest_entry["published_parsed"])
    )
    audio_url = latest_entry["media_content"][0]["url"]
    return Brief(
        guid=guid, title=title, published_time=published_time, audio_url=audio_url
    )


def download_audio(audio_url: str) -> BytesIO:
    logging.info("Downloading audio")
    audio_response = requests.get(audio_url)
    audio_data = BytesIO(audio_response.content)
    return audio_data
