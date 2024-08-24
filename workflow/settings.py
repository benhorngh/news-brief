import os

from dotenv import load_dotenv
from pydantic import BaseModel

from workflow import consts


class Settings(BaseModel):
    S3_BUCKET_NAME: str = ""
    RSS_PLAYLIST_NAME: str = ""
    RSS_URL: str = ""
    AUDIO_LANGUAGE_CODE: str = ""
    AUDIO_LANGUAGE: str = ""
    CLAUDE_API_KEY: str = ""
    TWITTER_TOKEN_KEY: str = ""
    TWITTER_TOKEN_SECRET: str = ""
    TWITTER_CONSUMER_KEY: str = ""
    TWITTER_CONSUMER_SECRET: str = ""
    TWITTER_BEARER: str = ""
    SECRETS_MANAGER_KEY: str = consts.SECRETS_MANAGER_KEY


settings = None


def init():
    load_dotenv()
    global settings
    settings = Settings(**os.environ)


init()
