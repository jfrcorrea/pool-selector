"""Módulo principal da API REST para seleção de pools de instâncias."""

import os

import duckdb
from fastapi import FastAPI

LOCALSTACK_PORT = os.environ.get("LOCALSTACK_PORT")
LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL")
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_FILE_NAME = os.environ["S3_FILE_NAME"]
AWS_KEY_ID = os.environ["AWS_KEY_ID"]
AWS_SECRET = os.environ["AWS_SECRET"]

# Cria uma secret para acessar o S3 a partir do DuckDB."""
endpoint = ""
if LOCALSTACK_URL is not None and LOCALSTACK_PORT is not None:
    endpoint = f"ENDPOINT '{LOCALSTACK_URL}:{LOCALSTACK_PORT}', URL_STYLE 'path', USE_SSL false,"
duckdb.sql(
    f"""
    CREATE SECRET s3_secret (
        TYPE S3,
        PROVIDER CREDENTIAL_CHAIN,
        CHAIN 'config',
        {endpoint}
        KEY_ID '{AWS_KEY_ID}',
        SECRET '{AWS_SECRET}'
    );
    """
)

app = FastAPI()


@app.get("/")
def read_root() -> dict:
    """Executa o endpoint raiz.

    Returns:
        dict: Um dict informando que o status do servidor está ok.
    """
    return {"status": "ok"}


@app.get("/get-pool")
def get_pool(instance_types: str | None = None) -> dict:
    """Retorna o pool de instâncias com melhor chance de executar um Spark Job.

    Args:
        instance_types (str | None, optional): Lista de tipos de instância que devem ser retornados. Default None.

    Returns:
        dict: Um dict com o pool_id mais indicado para o Spark Job. Formato: {"pool_id": "pool-r6.xlarge-us-east-1c"}.
    """
    where_clause = ""
    if instance_types:
        splitted_instance_types = str(tuple(instance_types.split(",")))
        where_clause = f"WHERE split_part(pool_id, '-', 2) in {splitted_instance_types}"
    result = duckdb.sql(
        f"""
        WITH cte as (
          SELECT pool_id,
                 COUNT(*) AS qtde,
                 COUNT(*) FILTER(reason = 'SPOT_INSTANCE_TERMINATION') AS qtde_spot_instance_termination
          FROM 's3://{S3_BUCKET_NAME}/{S3_FILE_NAME}'
          {where_clause}
          GROUP BY pool_id
        )
        SELECT pool_id
        FROM cte
        ORDER BY qtde_spot_instance_termination / qtde
        LIMIT 1;
        """
    ).fetchall()
    if result:
        row = result[0]
        return {"pool_id": row[0]}
    else:
        return {"pool_if": None}
