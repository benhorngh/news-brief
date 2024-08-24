import logging

import audio_service
import aws_service
import claude_service
import twitter_client
from logger_setup import init_logger
from settings import settings


def run():
    # details
    brief = audio_service.fetch_audio_details_from_rss(settings.RSS_URL)
    logging.info(f"Processing audio with id: {brief.guid}. Title: {brief.title}")
    if not aws_service.is_brief_file_exist(brief.guid):
        aws_service.upload_brief_details(brief.guid, brief)

    # audio
    if not aws_service.is_audio_file_exist(brief.guid):
        audio_bytes = audio_service.download_audio(brief.audio_url)
        aws_service.upload_audio(brief.guid, audio_bytes)
    else:
        logging.info("Audio already exist. skipping")

    # transcript
    if not aws_service.is_transcript_file_exist(brief.guid):
        transcript_bytes = aws_service.transcribe_audio(brief.guid)
        aws_service.upload_transcript(brief.guid, transcript_bytes)
    else:
        logging.info("Transcript already exist. skipping")
    transcript = aws_service.fetch_transcript(brief.guid)

    # headlines
    if not aws_service.is_headlines_file_exist(brief.guid):
        headlines = claude_service.summarize(transcript)
        aws_service.upload_headlines(brief.guid, headlines)
    else:
        logging.info("Headlines already exist. skipping")
    headlines = aws_service.fetch_headlines(brief.guid)

    # tweet
    if not aws_service.is_tweet_id_file_exist(brief.guid):
        tweet_id = twitter_client.tweet(brief, headlines)
        aws_service.upload_tweet_id(brief.guid, tweet_id)


if __name__ == "__main__":
    init_logger()
    run()
