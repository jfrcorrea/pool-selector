"""Aplicação para gerar eventos de teste."""

import random
import time
import os
from datetime import datetime, timezone
from uuid import uuid4

import boto3
import boto3.exceptions
import boto3.s3

import model

LOCALSTACK_PORT = os.environ["LOCALSTACK_PORT"]
LOCALSTACK_URL = os.environ["LOCALSTACK_URL"]
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_FILE_NAME = os.environ["S3_FILE_NAME"]


def get_s3_client() -> boto3.client:
    """Cria um Client S3.

    Returns:
        boto3.client: O Client S3 criado.
    """
    session = boto3.session.Session()
    s3_client = session.client(
        service_name="s3",
        aws_access_key_id="aaa",
        aws_secret_access_key="bbb",
        endpoint_url=f"http://{LOCALSTACK_URL}:{LOCALSTACK_PORT}",
    )

    return s3_client


def s3_append_data(s3_client: boto3.client, data: str) -> None:
    """Adiciona dados a um objeto no S3.

    Args:
        data (str): Os dados a serem adicionados.
    """
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_NAME)
        body = response.get("Body")
        object_data = body.read()
        object_data_str = object_data.decode()
    except s3_client.exceptions.NoSuchKey:
        object_data_str = ""

    if not object_data_str:
        object_data_str = data
    else:
        object_data_str += "\n" + data

    s3_client.put_object(Body=object_data_str.encode(), Bucket=S3_BUCKET_NAME, Key=S3_FILE_NAME)


def main() -> None:
    """Entrypoint do gerador de eventos de teste."""

    s3_client = get_s3_client()

    while True:
        status = random.choice(model.STATUS_LIST)
        event = model.SparkEvent(
            finished_at=datetime.now(timezone.utc).isoformat()[:-6],
            job_id=str(uuid4()),
            pool_id=f"pool-{random.choice(model.INSTANCE_TYPES)}-{random.choice(model.AZS)}",
            status=status,
            reason="" if status == "SUCCEEDED" else random.choice(model.REASON_LIST),
        )
        s3_append_data(s3_client=s3_client, data=event.to_json())
        time.sleep(random.random() * 3)


if __name__ == "__main__":
    main()
