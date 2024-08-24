import logging
from io import BytesIO
from time import sleep

import boto3
import botocore
import requests
from botocore.exceptions import ClientError

from workflow.models import Brief
from workflow.settings import settings

s3_client = boto3.client("s3")
transcribe_client = boto3.client("transcribe")


def upload_transcript(guid: str, transcript: str):
    object_key = get_transcript_file_key(guid)
    return _upload_text(object_key, transcript)


def upload_headlines(guid: str, headlines: list[str]):
    object_key = get_headlines_file_key(guid)
    headlines = "\n".join(headlines)
    return _upload_text(object_key, headlines)


def upload_tweet_id(guid: str, tweet_id: str):
    object_key = get_tweet_id_file_key(guid)
    return _upload_text(object_key, tweet_id)


def upload_brief_details(guid: str, brief: Brief):
    object_key = get_brief_file_key(guid)
    return _upload_json(object_key, brief.model_dump_json())


def fetch_transcript(guid: str) -> str:
    object_key = get_transcript_file_key(guid)
    return _fetch_text_file(object_key)


def fetch_headlines(guid: str) -> list[str]:
    object_key = get_headlines_file_key(guid)
    headlines = _fetch_text_file(object_key)
    return headlines.split("\n")


def get_audio_file_uri(guid: str) -> str:
    object_key = get_audio_file_key(guid)
    return f"s3://{settings.S3_BUCKET_NAME}/{object_key}"


def get_audio_file_key(guid: str) -> str:
    return f"{settings.RSS_PLAYLIST_NAME}/{guid}/audio.mp3"


def get_transcript_file_key(guid: str) -> str:
    return f"{settings.RSS_PLAYLIST_NAME}/{guid}/transcript.txt"


def get_headlines_file_key(guid: str) -> str:
    return f"{settings.RSS_PLAYLIST_NAME}/{guid}/headlines.txt"


def get_tweet_id_file_key(guid: str) -> str:
    return f"{settings.RSS_PLAYLIST_NAME}/{guid}/tweet_id.txt"


def get_brief_file_key(guid: str) -> str:
    return f"{settings.RSS_PLAYLIST_NAME}/{guid}/brief.json"


def is_audio_file_exist(guid: str) -> bool:
    object_key = get_audio_file_key(guid)
    return _is_object_exist(object_key)


def is_brief_file_exist(guid: str) -> bool:
    object_key = get_brief_file_key(guid)
    return _is_object_exist(object_key)


def is_transcript_file_exist(guid: str) -> bool:
    object_key = get_transcript_file_key(guid)
    return _is_object_exist(object_key)


def is_tweet_id_file_exist(guid: str) -> bool:
    object_key = get_tweet_id_file_key(guid)
    return _is_object_exist(object_key)


def is_headlines_file_exist(guid: str) -> bool:
    object_key = get_headlines_file_key(guid)
    return _is_object_exist(object_key)


def upload_audio(guid: str, file_content: BytesIO):
    object_key = get_audio_file_key(guid)
    file_content.seek(0)
    s3_client.upload_fileobj(
        Bucket=settings.S3_BUCKET_NAME,
        Key=object_key,
        Fileobj=file_content,
        ExtraArgs={"ContentType": "audio/mpeg"},
    )


def _upload_text(object_key: str, text: str):
    transcript_bytes = BytesIO(text.encode("utf-8"))
    transcript_bytes.seek(0)
    s3_client.upload_fileobj(
        Bucket=settings.S3_BUCKET_NAME,
        Key=object_key,
        Fileobj=transcript_bytes,
        ExtraArgs={"ContentType": "text/plain"},
    )


def _upload_json(object_key: str, json_file: str):
    transcript_bytes = BytesIO(json_file.encode("utf-8"))
    transcript_bytes.seek(0)
    s3_client.upload_fileobj(
        Bucket=settings.S3_BUCKET_NAME,
        Key=object_key,
        Fileobj=transcript_bytes,
        ExtraArgs={"ContentType": "application/json"},
    )


def _is_object_exist(object_key: str) -> bool:
    try:
        s3_client.head_object(Bucket=settings.S3_BUCKET_NAME, Key=object_key)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        logging.error(e.response["Error"])
        raise
    return True


def _fetch_text_file(object_key: str) -> str:
    file_data = BytesIO()
    s3_client.download_fileobj(
        Bucket=settings.S3_BUCKET_NAME, Key=object_key, Fileobj=file_data
    )
    file_data.seek(0)
    return file_data.read().decode("utf-8")


def transcribe_audio(guid: str) -> str:
    audio_uri = get_audio_file_uri(guid)
    transcribe_client.start_transcription_job(
        TranscriptionJobName=guid,
        Media={"MediaFileUri": audio_uri},
        MediaFormat="mp3",
        LanguageCode=settings.AUDIO_LANGUAGE_CODE,
    )
    transcript = None
    for i in range(1_000):
        transcription_job = transcribe_client.get_transcription_job(
            TranscriptionJobName=guid
        )
        status = transcription_job["TranscriptionJob"]["TranscriptionJobStatus"]
        if status == "FAILED":
            raise Exception("Transcription failed")
        if status == "COMPLETED":
            transcript = transcription_job["TranscriptionJob"]["Transcript"]
            break
        logging.info("Transcription still in progress...")
        sleep(5)
    if not transcript:
        raise Exception("Timeout on getting audio transcription")
    transcript_url = transcript["TranscriptFileUri"]
    transcript_response = requests.get(transcript_url)
    transcript_data = transcript_response.json()
    transcript_text = transcript_data["results"]["transcripts"][0]["transcript"]
    print(transcript_text)
    return transcript_text
