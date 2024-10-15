"""Módulo principal da API REST para seleção de pools de instâncias."""

import logging
import os

import duckdb
from fastapi import FastAPI, HTTPException

LOCALSTACK_PORT = os.environ.get("LOCALSTACK_PORT")
LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL")
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_FILE_NAME = os.environ["S3_FILE_NAME"]
AWS_KEY_ID = os.environ["AWS_KEY_ID"]
AWS_SECRET = os.environ["AWS_SECRET"]
EVENT_FILTER_WINDOW = os.environ["EVENT_FILTER_WINDOW"]
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Configuração dos logs
LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(threadName)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT, force=True)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

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
    """
    Retorna o pool de instâncias com melhor chance de executar um Spark Job.

    O pool retornado é aquele com o menor índice de erros por falta de Spot Instance.

    Args:
        instance_types (str | None, optional): Lista de tipos de instância para filtrar o retorno. Default None.

    Returns:
        dict: Um dict com o pool_id mais indicado para o Spark Job. Formato: {"pool_id": "pool-r6.xlarge-us-east-1c"}.
    """
    where_clause = make_where_clause()
    query = f"""
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
    logger.debug("Query: %s", query)

    try:
        result = duckdb.sql(query).fetchall()
        logger.debug("Query executada com sucesso")
    except Exception as e:
        logger.error("Query executada com erro: %s", e)
        raise HTTPException(status_code=500, detail="Erro interno ao executar consulta")

    if result:
        row = result[0]
        return {"pool_id": row[0]}
    else:
        return {"pool_if": None}


def make_where_clause(instance_types: str | None = None) -> str:
    """
    Cria a cláusula WHERE a ser aplicada na query do método `get_pool`.

    Esta cláusula leva em conta o filtro de tipos de instância e a janela de tempo para filtrar os eventos.

    Args:
        instance_types (str | None, optional): Ver o método `get_pool`. Default None.

    Returns:
        str: A cláusula WHERE pronta para ser aplicada na query.
    """

    where_clause = "WHERE 1 = 1"
    if instance_types:
        splitted_instance_types = str(tuple(instance_types.split(",")))
        where_clause += f" AND split_part(pool_id, '-', 2) in {splitted_instance_types}"

    if EVENT_FILTER_WINDOW:
        try:
            filter_window = int(EVENT_FILTER_WINDOW)
        except ValueError:
            logger.error(
                "A variável de ambiente `EVENT_FILTER_WINDOW` não é um número inteiro válido e será desconsiderada"
            )
            filter_window = 0
        if filter_window > 0:
            where_clause += f" AND CAST(finished_at AS TIMESTAMPTZ) >= now() - INTERVAL {EVENT_FILTER_WINDOW} SECOND"

    return where_clause


def setup_duckdb() -> None:
    """Configuração inicial do DuckDB."""

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
    logger.info("Secret criada no DuckDB")

    # Define o timezone do DuckDB como `UTC`
    duckdb.sql("SET timezone='UTC';")


if __name__ == "__main__":
    setup_duckdb()
