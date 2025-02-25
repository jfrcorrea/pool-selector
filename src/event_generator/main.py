"""Aplicação para gerar eventos de teste."""

import os
import random
import time
from datetime import datetime, timezone
from uuid import uuid4

import boto3
import boto3.exceptions
import boto3.s3

from event_generator import model

LOCALSTACK_PORT = os.environ.get("LOCALSTACK_PORT")
LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL")
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_FILE_NAME = os.environ["S3_FILE_NAME"]
AWS_KEY_ID = os.environ["AWS_KEY_ID"]
AWS_SECRET = os.environ["AWS_SECRET"]


def get_s3_client() -> boto3.client:
    """Cria um Client S3.

    Returns:
        boto3.client: O Client S3 criado.
    """
    session = boto3.session.Session()
    endpoint_url = None
    if LOCALSTACK_URL and LOCALSTACK_PORT:
        endpoint_url = f"http://{LOCALSTACK_URL}:{LOCALSTACK_PORT}"
    s3_client = session.client(
        service_name="s3",
        aws_access_key_id=AWS_KEY_ID,
        aws_secret_access_key=AWS_SECRET,
        endpoint_url=endpoint_url,
    )

    return s3_client


def s3_append_data(s3_client: boto3.client, data: str) -> None:
    """Adiciona dados a um objeto no S3.

    Args:
        s3_client (boto3.client): Client instanciado do S3.
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


def send_random_data(s3_client: boto3.client) -> None:
    """Envia um evento de Spark Job aleatório para o S3.

    Args:
        s3_client (boto3.client): Client instanciado do S3.
    """
    status = random.choice(model.STATUS_LIST)
    event = model.SparkEvent(
        finished_at=datetime.now(timezone.utc).isoformat()[:-6],
        job_id=str(uuid4()),
        pool_id=f"pool-{random.choice(model.INSTANCE_TYPES)}-{random.choice(model.AZS)}",
        status=status,
        reason="" if status == "SUCCEEDED" else random.choice(model.REASON_LIST),
    )
    s3_append_data(s3_client=s3_client, data=event.to_json())


def main() -> None:
    """
    Entrypoint do gerador de eventos de teste.

    Fica em um loop "eterno" gerando eventos aleatórios e salvando-os no arquivo do S3.
    """

    s3_client = get_s3_client()

    random.seed()

    while True:
        send_random_data(s3_client)
        time.sleep(random.random() * 2)  # Aguarda um intervalo entre 0 e 2 segundos


if __name__ == "__main__":
    main()
