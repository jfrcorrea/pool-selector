"""Testes unitários para o módulo web_app/utils."""

from unittest.mock import MagicMock, call, patch

from web_app import utils

utils.LOCALSTACK_PORT = "4566"
utils.LOCALSTACK_URL = "localstack"
utils.AWS_KEY_ID = "aaa"
utils.AWS_SECRET = "bbb"


def test_make_where_clause_no_filters() -> None:
    """Testa o método make_where_clause() sem filtros."""

    mock_logger = MagicMock()
    utils.EVENT_FILTER_WINDOW = "0"
    result = utils.make_where_clause(logger=mock_logger)

    assert result == "WHERE 1 = 1"


def test_make_where_clause_filter_window() -> None:
    """Testa o método make_where_clause() com o filtro de janela de tempo."""

    mock_logger = MagicMock()
    utils.EVENT_FILTER_WINDOW = "60"
    result = utils.make_where_clause(logger=mock_logger)

    assert result == "WHERE 1 = 1 AND CAST(finished_at AS TIMESTAMPTZ) >= now() - INTERVAL 60 SECOND"


def test_make_where_clause_filter_instance_type() -> None:
    """Testa o método make_where_clause() com o filtro de tipo de instância."""

    mock_logger = MagicMock()
    utils.EVENT_FILTER_WINDOW = "0"
    result = utils.make_where_clause(logger=mock_logger, instance_types="xpto")

    assert result == "WHERE 1 = 1 AND split_part(pool_id, '-', 2) in ('xpto',)"


def test_make_where_clause_filter_all_filters() -> None:
    """Testa o método make_where_clause() com todos os filtros juntos."""

    mock_logger = MagicMock()
    utils.EVENT_FILTER_WINDOW = "60"
    result = utils.make_where_clause(logger=mock_logger, instance_types="xpto")

    assert result == (
        "WHERE 1 = 1 AND split_part(pool_id, '-', 2) in ('xpto',) AND CAST(finished_at AS TIMESTAMPTZ) >= now() - "
        "INTERVAL 60 SECOND"
    )


def test_make_where_clause_filter_error() -> None:
    """Testa o método make_where_clause() com o filtro de janela de tempo errado."""

    mock_logger = MagicMock()
    utils.EVENT_FILTER_WINDOW = "XPTO"
    result = utils.make_where_clause(logger=mock_logger)

    assert result == "WHERE 1 = 1"


@patch("web_app.utils.duckdb")
def test_setup_duckdb(mock_duckdb: MagicMock) -> None:
    """Testa o método setup_duckdb()."""

    mock_logger = MagicMock()
    utils.setup_duckdb(logger=mock_logger)

    calls = [
        call(
            f"""
        CREATE SECRET s3_secret (
            TYPE S3,
            PROVIDER CREDENTIAL_CHAIN,
            CHAIN 'config',
            ENDPOINT '{utils.LOCALSTACK_URL}:{utils.LOCALSTACK_PORT}', URL_STYLE 'path', USE_SSL false,
            KEY_ID '{utils.AWS_KEY_ID}',
            SECRET '{utils.AWS_SECRET}'
        );
        """
        ),
        call("SET timezone='UTC';"),
    ]
    mock_duckdb.sql.assert_has_calls(calls)
