import logging

import tweepy

from models import Brief
from settings import settings

x_client = tweepy.Client(
    bearer_token=settings.TWITTER_BEARER,
    access_token=settings.TWITTER_TOKEN_KEY,
    access_token_secret=settings.TWITTER_TOKEN_SECRET,
    consumer_key=settings.TWITTER_CONSUMER_KEY,
    consumer_secret=settings.TWITTER_CONSUMER_SECRET,
)


def tweet(brief: Brief, headlines: list[str]) -> str:
    content = f"{brief.title}\n"
    first_tweet_id = None
    latest_tweet_id = None
    for headline in headlines:
        headline = headline.strip()
        if not headline:
            continue
        headline = f"\n- {headline}"
        if len(content) + len(headline) >= 250:
            latest_tweet_id = _post_tweet(content, latest_tweet_id)
            if first_tweet_id is None:
                first_tweet_id = latest_tweet_id
            content = headline
        else:
            content += headline
    return first_tweet_id


def _post_tweet(content: str, in_reply_to_tweet_id: str):
    logging.info("Posting a new tweet")
    post_id = x_client.create_tweet(
        text=content, in_reply_to_tweet_id=in_reply_to_tweet_id
    ).data["id"]
    logging.info("Tweet successfully posted")
    return post_id
