"""Módulo principal da API REST para seleção de pools de instâncias."""

import logging
import os

import duckdb
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from . import utils

S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_FILE_NAME = os.environ["S3_FILE_NAME"]
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Configuração dos logs
LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(threadName)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT, force=True)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

utils.setup_duckdb(logger)

app = FastAPI()


@app.get("/")
def read_root() -> dict:
    """Executa o endpoint raiz.

    Returns:
        dict: Um dict informando que o status do servidor está ok.
    """
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    """Retorna o favicon.ico.

    Returns:
        FileResponse: Uma instância da classe FileResponse apontando para o favicon.
    """
    return FileResponse("favicon.ico")


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
    where_clause = utils.make_where_clause(logger, instance_types)
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
