"""Conjunto de métodos auxiliares."""

import logging
import os

import duckdb

LOCALSTACK_PORT = os.environ.get("LOCALSTACK_PORT")
LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL")
AWS_KEY_ID = os.environ["AWS_KEY_ID"]
AWS_SECRET = os.environ["AWS_SECRET"]
EVENT_FILTER_WINDOW = os.environ["EVENT_FILTER_WINDOW"]


def make_where_clause(logger: logging.Logger, instance_types: str | None = None) -> str:
    """
    Cria a cláusula WHERE a ser aplicada na query do método `get_pool`.

    Esta cláusula leva em conta o filtro de tipos de instância e a janela de tempo para filtrar os eventos.

    Args:
        logger (logging.Logger): Objeto logger principal.
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


def setup_duckdb(logger: logging.Logger) -> None:
    """
    Configuração inicial do DuckDB.

    Args:
        logger (logging.Logger): Objeto logger principal.
    """

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
