import json
import os

import boto3
from botocore.exceptions import ClientError

from workflow import settings


def update_secrets():
    secrets = _fetch_secret(settings.settings.SECRETS_MANAGER_KEY)
    for key, value in secrets.items():
        os.environ[key] = value
    settings.init()


def _fetch_secret(secret_id: str):
    secrets_client = boto3.client("secretsmanager")

    try:
        get_secret_value_response = secrets_client.get_secret_value(SecretId=secret_id)
        secrets = json.loads(get_secret_value_response.get("SecretString"))
    except ClientError as e:
        raise e
    if not secrets:
        raise Exception(
            f"Failed to fetch secrets from AWS secrets manager: {get_secret_value_response}"
        )
    return secrets
